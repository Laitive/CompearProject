# 导入CMDpassword模块
import CMDpassword

while CMDpassword.umv != 0:
    # 显示模式信息
    if(CMDpassword.tag == True):
        print('this is root mode \n this mode can break this project so please care for it')
    else:
        print('this is user mode \n this mode can not break this project')
    
    # 显示当前配置信息
    print(f"当前配置: {CMDpassword.config}")
    
    # 获取用户输入
    a = str(input("控制代码: "))
    
    # 处理命令
    if(a == 'exit'):
        break
    elif(a == 'change-root'):
        CMDpassword.tag = True
        pwd = str(input('请输入密码: '))
        if(pwd != CMDpassword.password):
            CMDpassword.tag = False
            print('密码错误 Cannot change to root')
        else:
            print('密码正确')
    elif(a == 'change-user'):
        CMDpassword.tag = False
        pwd = str(input('请输入密码: '))
        if(pwd != CMDpassword.password):
            CMDpassword.tag = True
            print('密码错误 Cannot change to user')
        else:
            print('密码正确')
            CMDpassword.tag = False
            print('切换为用户模式')
    elif(a == 'change-password'):
        pwd = str(input('请输入旧密码: '))
        new_pwd = str(input('请输入新密码: '))
        success, message = CMDpassword.change_password(pwd, new_pwd)
        print(message)
    elif(a == 'show-config'):
        # 显示所有配置项
        print("配置项列表:")
        for key, value in CMDpassword.config.items():
            print(f"  {key}: {value}")
    elif(a == 'add-config'):
        # 添加新的配置项
        if CMDpassword.tag:  # 只允许root模式添加配置
            key = input("请输入配置项名称: ")
            value = input("请输入配置项值: ")
            CMDpassword.config[key] = value
            CMDpassword.save_all_config(CMDpassword.config)
            print(f"配置项 '{key}' 添加成功")
        else:
            print("用户模式下无法添加配置项，请切换到root模式")
    elif(a == 'delete-config'):
        # 删除配置项
        if CMDpassword.tag:  # 只允许root模式删除配置
            key = input("请输入要删除的配置项名称: ")
            if key in CMDpassword.config and key != 'password':  # 不允许删除密码项
                del CMDpassword.config[key]
                CMDpassword.save_all_config(CMDpassword.config)
                print(f"配置项 '{key}' 删除成功")
            elif key == 'password':
                print("密码配置项不允许删除")
            else:
                print(f"配置项 '{key}' 不存在")
        else:
            print("用户模式下无法删除配置项，请切换到root模式")
    elif(a == 'update-config'):
        # 更新配置项
        if CMDpassword.tag:  # 只允许root模式更新配置
            key = input("请输入要更新的配置项名称: ")
            if key in CMDpassword.config:
                value = input(f"请输入 '{key}' 的新值: ")
                CMDpassword.config[key] = value
                CMDpassword.save_all_config(CMDpassword.config)
                print(f"配置项 '{key}' 更新成功")
                # 如果更新的是密码，同步更新password变量
                if key == 'password':
                    CMDpassword.password = value
            else:
                print(f"配置项 '{key}' 不存在")
        else:
            print("用户模式下无法更新配置项，请切换到root模式")
    elif(a == 'show-password'):
        # 显示密码
        if CMDpassword.tag:
            print(f"当前密码: {CMDpassword.password}")
        else:
            print("用户模式下无法显示密码，请切换到root模式")
    elif(a == 'admin32'):
        # 管理员模式
        if CMDpassword.tag:
            print("管理员模式已激活")
            CMDpassword.admin=True
        else:
            print("用户模式下无法激活管理员模式，请切换到root模式")
    else:
        print(f"未知命令: {a}")
    
    # 在每次循环结束后更新配置文件（确保文件内容与内存中的配置一致）
    CMDpassword.save_all_config(CMDpassword.config)