from mac_validator import (
    get_mac_address_py,
    encrypt_info,
    encrypt_info_custom,
    verify_info,
    verify_info_custom
)

def test_basic_functions():
    print("\n=== 基础功能测试 ===")
    # 获取MAC地址
    mac = get_mac_address_py()
    print(f"本机MAC地址: {mac}")

    # 加密MAC地址（7天有效期）
    encrypted = encrypt_info()
    print(f"加密信息（7天有效）: {encrypted}")

    # 验证加密信息
    mac_mismatch, expired = verify_info(encrypted)
    print(f"MAC地址是否不匹配: {mac_mismatch}")
    print(f"是否已过期: {expired}")

def test_custom_functions():
    print("\n=== 自定义功能测试 ===")
    # 测试自定义MAC地址和有效期
    test_mac = "[00, 11, 22, 33, 44, 55]"
    days = -1
    print(f"自定义MAC地址: {test_mac}")
    print(f"自定义有效天数: {days}")

    # 加密自定义MAC地址
    encrypted_custom = encrypt_info_custom(test_mac, days)
    print(f"自定义加密信息: {encrypted_custom}")

    # 验证自定义MAC地址
    mac_mismatch, expired = verify_info_custom(encrypted_custom, test_mac)
    print(f"自定义MAC是否不匹配: {mac_mismatch}")
    print(f"自定义是否已过期: {expired}")

    # 测试错误的MAC地址
    wrong_mac = "[FF, FF, FF, FF, FF, FF]"
    mac_mismatch, expired = verify_info_custom(encrypted_custom, wrong_mac)
    print(f"\n错误MAC地址测试: {wrong_mac}")
    print(f"错误MAC是否不匹配: {mac_mismatch}")
    print(f"错误MAC是否已过期: {expired}")

def test_error_cases():
    print("\n=== 错误场景测试 ===")
    try:
        # 测试无效的加密信息
        invalid_encrypted = "invalid_base64_string"
        verify_info(invalid_encrypted)
    except Exception as e:
        print(f"无效加密信息异常: {str(e)}")

    try:
        # 测试无效的MAC地址格式
        invalid_mac = "invalid_mac_format"
        encrypt_info_custom(invalid_mac, 7)
    except Exception as e:
        print(f"无效MAC地址格式异常: {str(e)}")

if __name__ == "__main__":
    print("开始运行MAC校验器测试...")
    test_basic_functions()
    test_custom_functions()
    test_error_cases()
    print("\n所有测试已完成！") 