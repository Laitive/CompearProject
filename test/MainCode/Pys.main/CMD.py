# 导入CMDpassword模块
import CMDpassword
import json

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
    elif(a == '/?'):
        # 显示帮助信息
        print("\n=== 命令帮助 ===")
        print("exit - 退出程序")
        print("change-root - 切换到root模式（需要密码）")
        print("change-user - 切换到user模式（需要密码）")
        print("change-password - 修改密码（需要旧密码）")
        print("show-config - 显示所有配置项")
        print("add-config - 添加新的配置项（仅root模式）")
        print("delete-config - 删除配置项（仅root模式，不允许删除密码）")
        print("update-config - 更新配置项（仅root模式）")
        print("show-password - 显示当前密码（仅root模式）")
        print("admin32 - 激活管理员模式（仅root模式）")
        print("show-website-config - 显示网站配置（仅root模式）")
        print("update-website-config - 更新网站配置（仅root模式）")
        print("list-website-sections - 列出所有网站配置部分（仅root模式）")
        print("start-website - 启动网站服务（仅root模式）")
        print("stop-website - 关闭网站服务（仅root模式）")
        print("check-website - 检查网站服务状态")
        print("/? - 显示此帮助信息")
        print("==============\n")
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
    elif(a == 'show-website-config'):
        # 显示网站配置
        if CMDpassword.tag:  # 只允许root模式查看
            section = input("请输入要查看的配置部分名称（如site, hero等，留空查看全部）: ").strip()
            success, result = CMDpassword.show_website_config_section(None if section == '' else section)
            if success:
                print("网站配置:")
                # 格式化输出配置
                import json
                print(json.dumps(result, ensure_ascii=False, indent=4))
            else:
                print(result)
        else:
            print("用户模式下无法查看网站配置，请切换到root模式")
    elif(a == 'update-website-config'):
        # 更新网站配置
        if CMDpassword.tag:  # 只允许root模式更新
            section = input("请输入要更新的配置部分名称（如site, hero等）: ").strip()
            key = input("请输入要更新的配置项名称: ").strip()
            value = input("请输入新的配置值: ").strip()
            
            # 尝试将值转换为JSON类型（如数字、布尔值等）
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                # 如果不是有效的JSON，保持字符串形式
                pass
            
            success, message = CMDpassword.update_website_config_section(section, key, value)
            print(message)
        else:
            print("用户模式下无法更新网站配置，请切换到root模式")
    elif(a == 'list-website-sections'):
        # 列出所有网站配置部分
        if CMDpassword.tag:  # 只允许root模式
            success, config_data = CMDpassword.show_website_config_section()
            if success:
                print("网站配置部分列表:")
                for section_name in config_data.keys():
                    print(f"  - {section_name}")
            else:
                print(config_data)
        else:
            print("用户模式下无法列出网站配置部分，请切换到root模式")
    elif(a == 'start-website'):
        # 启动网站服务
        if CMDpassword.tag:  # 只允许root模式启动
            success, message = CMDpassword.start_website()
            print(message)
        else:
            print("用户模式下无法启动网站，请切换到root模式")
    elif(a == 'stop-website'):
        # 关闭网站服务
        if CMDpassword.tag:  # 只允许root模式关闭
            success, message = CMDpassword.stop_website()
            print(message)
        else:
            print("用户模式下无法关闭网站，请切换到root模式")
    elif(a == 'check-website'):
        # 检查网站服务状态
        success, message = CMDpassword.check_website_status()
        print(message)
    else:
        print(f"未知命令: {a}")
    
    # 在每次循环结束后更新配置文件（确保文件内容与内存中的配置一致）
    CMDpassword.save_all_config(CMDpassword.config)