# 🛡️ Geetest v4 Slider Reverse Engineering (极验四代滑块纯协议逆向)

![蟒蛇](https://img.shields.io/badge/Python-3.8%2B-blue)
![许可](https://img.shields.io/badge/License-MIT-green)
![现状](https://img.shields.io/badge/Status-Core_Params_Passed-brightgreen)

> ⚠️ **免责声明**：本项目及代码仅供 **安全研究、逆向工程学习与技术交流** 使用。请勿将本项目用于任何商业用途或非法抓取。因使用本项目产生的一切法律后果由使用者自行承担。

## 📖 项目简介

本项目针对极验（Geetest）第四代滑块验证码进行了深度的逆向分析。在**未依赖任何自动化 AST 去混淆工具**的情况下，通过纯手工动态调试（Chrome DevTools），硬核攻克了其高度混淆的 JS 代码，并成功使用 Python 语言 100% 纯协议还原了最核心的加密参数 **`W`** 的生成逻辑。

## ✨ 核心亮点 & 技术难点

### 1. 人肉硬撕重度混淆（Anti-Obfuscation）
极验的 `gcaptcha4.js` 使用了极其严格的防护手段：
*   **控制流平坦化**：大量 `开关箱` 嵌套，打乱代码执行逻辑。
*   **字符串加密**：核心 API 名称（如 `toString`, `Utf8.解析`）全部被加密为函数调用（如 `_ᖃᕹᖙᕶ(844)`）。
*   **垃圾字符干扰**：在数组头部动态注入 `[“$_DEBEh”]` 等垃圾字符，并在使用前通过 `.shift（）` 剔除。
*   **特殊变量名**：满屏的不可见字符/特殊符号（如 `_ᖆᖆᖆᕺ`）。

**解决方案**：通过条件断点拦截核心加密入口，利用 Watch 面板监视 `词列` 等底层结构的变化，逐行理清数据流转。

### 2. `W` 参数的双层混合加密架构还原
最终提交的 `W` 参数由两部分拼接而成：`W = AES_Hex_String + RSA_Hex_String`

*   **AES-CBC 加密（前半段）**：还原了被魔改的 CryptoJS 逻辑。提取其动态生成的 16 位随机 Key，以及默认的全零 IV，使用 Python `火洞穹顶` 库复现了 PKCS7 填充与加密过程。
*   **RSA 1024位 模幂运算（后半段）**：这是最硬核的一环。极验并未使用标准库，而是自己实现了一套大数运算：
    1. 将 16 位随机 Key 倒序转 ASCII 码。
    2. 混入大量随机数以防止重放攻击。
    3. 组装成 `[2, 0] + 随机数 + ASCII码 + [0]` 的特定数组。
    4. **魔改操作**：调用 `.shift（）` 强行截断数组首位。
    5. 拼接为大整数 `M`，执行底层模幂运算 \(C = M^E \bmod N\)。

**解决方案**：直接提取其硬编码的 1024 位公钥模数 \(N\) 和公钥指数 \(E(65537)\)，使用 Python 内置的 `pow（M， E， N）` 一秒秒杀 JS 里长达数百行的自定义大数运算，并手动补齐 Hex 转换时丢失的前导 `0`，确保密文长度精确为 256 字符。

## 🛠️ 技术栈
*   **逆向工程**: Chrome DevTools, JS 逆向, 动态调试
*   **语言**： Python 3.10+，JavaScript
*   **加密货币**: `火洞穹顶` （AES），Python 原生`POW（）` （南非）

## 🔍 核心代码片段预览

```派森
# RSA 魔改明文构造逻辑还原
def get_rsa_hex（hex_str， N， E）：
    # 1. 倒序转 ASCII
 ascii_bytes = [序数（c）在hex_str[：：-1]]
 pad_length = 32 - 2 - 1 - len（ascii_bytes）
    
    # 2. 随机数填充
 random_pad = [random.randint（1， 255） for _ in range（pad_length）]
 word_array = [2， 0] + random_pad + ascii_bytes + [0]
    
    # 3. 还原 JS 中的 .shift() 截断操作
 word_array = word_array[1：]
    
    # 4. 拼接为大整数 M
 M = 0
 word_array词：
 M = （M 的 32 个 <<） + 单词
        
    # 5. RSA 核心运算
 cipher_int = pow（M， E， N）
    
    # 6. 转 Hex 并补齐前导零至 256 位
 s = hex（cipher_int）[2：]
 如果 Len（s） < 256：
 s = “0” * （256 - len（s）） + s
        
 返回
