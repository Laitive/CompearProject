#include <QApplication>
#include <QMainWindow>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QTextEdit>
#include <QLineEdit>
#include <QPushButton>
#include <QProcess>
#include <QString>
#include <QStringList>
#include <QFileDialog>
#include <QMessageBox>
#include <QTabWidget>
#include <QComboBox>
#include <QLabel>
#include <QScrollBar>
#include <QKeyEvent>
#include <QSettings>
#include <QDir>

// 自定义的QTextEdit类，用于捕获键盘事件
class TerminalTextEdit : public QTextEdit {
    Q_OBJECT

public:
    TerminalTextEdit(QWidget *parent = nullptr) : QTextEdit(parent) {
        setReadOnly(true);
        setUndoRedoEnabled(false);
        commandPosition = textCursor().position();
    }

protected:
    // 捕获键盘事件
    void keyPressEvent(QKeyEvent *event) override {
        QTextCursor cursor = textCursor();
        int currentPos = cursor.position();

        // 如果光标在命令输入区域之前，移动到命令输入区域末尾
        if (currentPos < commandPosition) {
            cursor.setPosition(document()->characterCount() - 1);
            setTextCursor(cursor);
        }

        // 处理不同的按键
        if (event->key() == Qt::Key_Return || event->key() == Qt::Key_Enter) {
            // 回车键：发送命令
            emit commandEntered(getCurrentCommand());
            append("\n");
            commandPosition = textCursor().position();
        } else if (event->key() == Qt::Key_Backspace) {
            // 退格键：如果在命令输入区域内，允许删除
            if (currentPos > commandPosition) {
                QTextEdit::keyPressEvent(event);
            }
        } else {
            // 其他键：正常处理
            QTextEdit::keyPressEvent(event);
        }
    }

public slots:
    // 输出文本到终端
    void appendOutput(const QString &text) {
        append(text);
        // 自动滚动到底部
        QScrollBar *scrollBar = verticalScrollBar();
        scrollBar->setValue(scrollBar->maximum());
        commandPosition = textCursor().position();
    }

    // 获取当前输入的命令
    QString getCurrentCommand() {
        QTextCursor cursor = textCursor();
        cursor.setPosition(commandPosition);
        cursor.movePosition(QTextCursor::End, QTextCursor::KeepAnchor);
        return cursor.selectedText();
    }

signals:
    // 命令输入完成的信号
    void commandEntered(const QString &command);

private:
    // 命令输入区域的起始位置
    int commandPosition;
};

// 主窗口类
class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr)
        : QMainWindow(parent) {
        setWindowTitle("Qt Terminal with Config");
        setMinimumSize(800, 600);

        // 创建中心部件
        QWidget *centralWidget = new QWidget(this);
        setCentralWidget(centralWidget);

        // 创建主布局
        QVBoxLayout *mainLayout = new QVBoxLayout(centralWidget);

        // 创建选项卡控件
        QTabWidget *tabWidget = new QTabWidget(this);
        mainLayout->addWidget(tabWidget);

        // 创建终端选项卡
        QWidget *terminalTab = createTerminalTab();
        tabWidget->addTab(terminalTab, "终端");

        // 创建配置选项卡
        QWidget *configTab = createConfigTab();
        tabWidget->addTab(configTab, "配置");

        // 创建状态栏
        statusBar()->showMessage("就绪");

        // 加载设置
        loadSettings();
        
        // 启动CMD进程
        startCmdProcess();
    }

    ~MainWindow() {
        // 确保进程被终止
        if (cmdProcess && cmdProcess->state() == QProcess::Running) {
            cmdProcess->terminate();
            cmdProcess->waitForFinished(1000);
            if (cmdProcess->state() == QProcess::Running) {
                cmdProcess->kill();
            }
        }

        // 保存设置
        saveSettings();
    }

private slots:
    // 处理命令输入
    void handleCommand(const QString &command) {
        if (!cmdProcess || cmdProcess->state() != QProcess::Running) {
            terminal->appendOutput("错误: CMD进程未运行");
            return;
        }

        // 显示命令并发送到CMD进程
        QString commandWithLineEnding = command + "\n";
        cmdProcess->write(commandWithLineEnding.toLocal8Bit());
    }

    // 读取CMD进程的标准输出
    void readCmdOutput() {
        if (cmdProcess) {
            QByteArray output = cmdProcess->readAllStandardOutput();
            if (!output.isEmpty()) {
                terminal->appendOutput(QString::fromLocal8Bit(output));
            }
        }
    }

    // 读取CMD进程的标准错误
    void readCmdError() {
        if (cmdProcess) {
            QByteArray error = cmdProcess->readAllStandardError();
            if (!error.isEmpty()) {
                terminal->appendOutput(QString::fromLocal8Bit("错误: " + error));
            }
        }
    }

    // 处理CMD进程的状态变化
    void handleProcessStateChange(QProcess::ProcessState newState) {
        switch (newState) {
            case QProcess::Running:
                statusBar()->showMessage("CMD进程正在运行");
                break;
            case QProcess::NotRunning:
                statusBar()->showMessage(QString("CMD进程已停止 (退出码: %1)").arg(cmdProcess->exitCode()));
                terminal->appendOutput("CMD进程已停止");
                break;
            case QProcess::Starting:
                statusBar()->showMessage("正在启动CMD进程...");
                break;
        }
    }

    // 处理CMD进程的错误
    void handleProcessError(QProcess::ProcessError error) {
        QString errorMessage;
        switch (error) {
            case QProcess::FailedToStart:
                errorMessage = "CMD进程启动失败: 找不到程序或权限不足";
                break;
            case QProcess::Crashed:
                errorMessage = "CMD进程崩溃";
                break;
            case QProcess::Timedout:
                errorMessage = "CMD进程超时";
                break;
            default:
                errorMessage = "CMD进程发生未知错误";
                break;
        }
        QMessageBox::critical(this, "错误", errorMessage);
        terminal->appendOutput(errorMessage);
    }

    // 重新启动CMD进程
    void restartCmdProcess() {
        if (cmdProcess && cmdProcess->state() == QProcess::Running) {
            cmdProcess->terminate();
            cmdProcess->waitForFinished(1000);
        }
        startCmdProcess();
    }

    // 选择配置文件目录
    void selectConfigDir() {
        QString dir = QFileDialog::getExistingDirectory(this, "选择配置文件目录", configDirComboBox->currentText());
        if (!dir.isEmpty()) {
            configDirComboBox->setCurrentText(dir);
        }
    }

    // 加载配置文件
    void loadConfigFile() {
        QString fileName = QFileDialog::getOpenFileName(this, "打开配置文件", configDirComboBox->currentText(), "配置文件 (*.dir *.config)");
        if (!fileName.isEmpty()) {
            // 这里可以添加加载配置文件的代码
            terminal->appendOutput(QString("已选择配置文件: %1").arg(fileName));
            QMessageBox::information(this, "配置", QString("配置文件已选择: %1\n\n在实际应用中，这里会加载配置文件的内容并应用到程序中。").arg(fileName));
        }
    }

private:
    TerminalTextEdit *terminal;  // 终端文本区域
    QProcess *cmdProcess;       // CMD进程
    QComboBox *configDirComboBox; // 配置目录选择框

    // 创建终端选项卡
    QWidget* createTerminalTab() {
        QWidget *widget = new QWidget(this);
        QVBoxLayout *layout = new QVBoxLayout(widget);

        // 创建终端文本区域
        terminal = new TerminalTextEdit(this);
        layout->addWidget(terminal);

        // 创建控制按钮布局
        QHBoxLayout *buttonLayout = new QHBoxLayout();

        // 创建重启按钮
        QPushButton *restartButton = new QPushButton("重启CMD", this);
        connect(restartButton, &QPushButton::clicked, this, &MainWindow::restartCmdProcess);
        buttonLayout->addWidget(restartButton);

        // 添加水平弹簧
        buttonLayout->addStretch();

        // 添加按钮布局到主布局
        layout->addLayout(buttonLayout);

        // 连接命令输入信号
        connect(terminal, &TerminalTextEdit::commandEntered, this, &MainWindow::handleCommand);

        return widget;
    }

    // 创建配置选项卡
    QWidget* createConfigTab() {
        QWidget *widget = new QWidget(this);
        QVBoxLayout *layout = new QVBoxLayout(widget);

        // 创建配置目录选择
        QHBoxLayout *configDirLayout = new QHBoxLayout();
        QLabel *configDirLabel = new QLabel("配置目录:", this);
        configDirComboBox = new QComboBox(this);
        configDirComboBox->addItem("c:/Users/Administrator/Documents/GitHub/CompearProject/ConfigDir");
        QPushButton *browseButton = new QPushButton("浏览...", this);
        
        connect(browseButton, &QPushButton::clicked, this, &MainWindow::selectConfigDir);
        
        configDirLayout->addWidget(configDirLabel);
        configDirLayout->addWidget(configDirComboBox);
        configDirLayout->addWidget(browseButton);

        // 创建加载配置文件按钮
        QPushButton *loadConfigButton = new QPushButton("加载配置文件", this);
        connect(loadConfigButton, &QPushButton::clicked, this, &MainWindow::loadConfigFile);

        // 创建配置信息文本区域
        QTextEdit *configInfoTextEdit = new QTextEdit(this);
        configInfoTextEdit->setReadOnly(true);
        configInfoTextEdit->setHtml(
            "<h3>配置说明</h3>" 
            "<p>本应用程序支持以下功能：</p>" 
            "<ul>" 
            "<li>集成CMD终端功能</li>" 
            "<li>配置文件目录选择</li>" 
            "<li>配置文件加载</li>" 
            "<li>在实际应用中，您可以扩展此界面以支持更多配置选项</li>" 
            "</ul>"
        );

        // 添加所有组件到布局
        layout->addLayout(configDirLayout);
        layout->addWidget(loadConfigButton);
        layout->addWidget(configInfoTextEdit);

        return widget;
    }

    // 启动CMD进程
    void startCmdProcess() {
        // 创建CMD进程
        cmdProcess = new QProcess(this);

        // 连接信号和槽
        connect(cmdProcess, &QProcess::readyReadStandardOutput, this, &MainWindow::readCmdOutput);
        connect(cmdProcess, &QProcess::readyReadStandardError, this, &MainWindow::readCmdError);
        connect(cmdProcess, &QProcess::stateChanged, this, &MainWindow::handleProcessStateChange);
        connect(cmdProcess, &QProcess::errorOccurred, this, &MainWindow::handleProcessError);

        // 在Windows上启动cmd.exe
        cmdProcess->start("cmd.exe");

        // 显示启动信息
        terminal->appendOutput("正在启动CMD...\n");
    }

    // 保存设置
    void saveSettings() {
        QSettings settings("QtTerminalApp", "Settings");
        settings.setValue("configDir", configDirComboBox->currentText());
        settings.setValue("windowSize", size());
        settings.setValue("windowPos", pos());
    }

    // 加载设置
    void loadSettings() {
        QSettings settings("QtTerminalApp", "Settings");
        QString configDir = settings.value("configDir", "c:/Users/Administrator/Documents/GitHub/CompearProject/ConfigDir").toString();
        configDirComboBox->setCurrentText(configDir);

        QSize size = settings.value("windowSize", QSize(800, 600)).toSize();
        resize(size);

        QPoint pos = settings.value("windowPos", QPoint(100, 100)).toPoint();
        move(pos);
    }
};

#include "qt_terminal_app.moc"

// 主函数
int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    app.setApplicationName("Qt Terminal with Config");
    app.setApplicationVersion("1.0.0");

    MainWindow mainWindow;
    mainWindow.show();

    return app.exec();
}