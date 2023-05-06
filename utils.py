import re
import sympy as sp


symbol = {
    'PI': sp.pi,
    'E': sp.E,
    'sqrt': lambda expr: sp.sqrt(expr),
    'factor': lambda expr: sp.factorial(expr),
    'sin': lambda expr: sp.sin(expr),
    'cos': lambda expr: sp.cos(expr),
    'tan': lambda expr: sp.tan(expr),
    'log': lambda expr, base=sp.E: sp.log(expr, base),
    'diff': lambda expr, var: sp.diff(expr, var),
    'integrate': lambda expr, var: sp.integrate(expr, var),
}
builtin_symbol = symbol.copy()
keywords = set(symbol.keys())   # 內建關鍵字
instructions = {'reset_all', 'reset '}
callback_clear_history = lambda: None   # mainUI._clear_history 的 callback function


def word_correction(text: str):
    text = text.replace("座", "左")
    text = text.replace("又掛號", "右括號")
    text = text.replace("掛號", "括號")
    text = text.replace("家居", "加g")
    text = text.replace("家具", "加g")
    text = text.replace("與賢", "餘弦")
    text = text.replace("與先", "餘弦")
    text = text.replace("階層", "階乘")
    text = text.replace("階成分之", "階乘分之")
    return text


def has_instruction(text: str):
    for instr in instructions:
        if text.find(instr) != -1:
            return True
    return False


def chinese_to_arabic(zh_num):
    zh2digit_table = {'零': 0, '一': 1, '二': 2, '兩': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
                      '十': 10, '百': 100, '千': 1000, '〇': 0, '○': 0, '０': 0, '１': 1, '２': 2, '３': 3, '４': 4,
                      '５': 5, '６': 6, '７': 7, '８': 8, '９': 9, '壹': 1, '貳': 2, '參': 3, '肆': 4, '伍': 5, '陆': 6,
                      '柒': 7, '捌': 8, '玖': 9, '拾': 10, '佰': 100, '仟': 1000, '萬': 10000, '億': 100000000}
    digit_num = 0
    # 結果
    result = 0
    # 暫時存儲的變量
    tmp = 0
    # 億的個數
    billion = 0
    while digit_num < len(zh_num):
        tmp_zh = zh_num[digit_num]
        tmp_num = zh2digit_table.get(tmp_zh, None)
        if tmp_num == 100000000:
            result = result + tmp
            result = result * tmp_num
            billion = billion * 100000000 + result
            result = 0
            tmp = 0
        elif tmp_num == 10000:
            result = result + tmp
            result = result * tmp_num
            tmp = 0
        elif tmp_num >= 10:
            if tmp == 0:
                tmp = 1
            result = result + tmp_num * tmp
            tmp = 0
        elif tmp_num is not None:
            tmp = tmp * 10 + tmp_num
        digit_num += 1
    result = result + tmp
    result = result + billion
    return result


def find_corresponding_bracket(pos: int, text: str):
    accu = step = 1 if text[pos] == '(' else -1 if text[pos] == ')' else 0
    while accu:
        pos += step
        if text[pos] == '(':
            accu += 1
        elif text[pos] == ')':
            accu -= 1
    return pos


def translate_to_standard(text: str):
    """
    將輸入的自然敘述句翻譯為標準敘述句，以供 execute() 作運算式處理
    因為目的為只要可以將合法的自然敘述句標準化就好，故此函式沒有義務檢查敘述句的語法是否正確，只要假設語法為正確的來做設計
    但有順便檢查括號合不合法
    不改 symbol
    """

    """
    # 處理指令
    """
    text = text.replace("重設全部", "reset_all")
    text = text.replace("reset all", "reset_all")
    text = text.replace("重設未知數", "reset ")
    text = text.replace("重設", "reset ")
    # 將指令換成代號，到最後才會換回來
    for idx, word in enumerate(instructions):
        text = text.replace(word, '$<' + str(idx) + '>')

    """
    # 去掉空白
    """
    text = text.replace(" ", "")

    """
    # 中文數字轉阿拉伯數字
    """
    while True:
        match = re.search(r'[零一二兩三四五六七八九十百千〇○０１２３４５６７８９壹貳參肆伍陆柒捌玖拾佰仟萬億]+', text)
        if match:
            text = text[:match.start()] + str(chinese_to_arabic(match.group())) + text[match.end():]
        else:
            break
    text = text.replace("點", ".")

    """
    # 設定變數大小寫: 如 A+k大a -> a+kA
    """
    # 將關鍵字轉換成代號，避免被轉小寫 (還是中文的關鍵字不用換沒關係 不會被轉)
    for idx, word in enumerate(keywords):
        text = text.replace(word, '$"' + str(idx) + '"')
    text = text.lower()
    while True:
        match = re.search(r'大([a-z]\d*)', text)
        if match:
            text = text[:match.start()] + match.groups()[0].upper() + text[match.end():]
        else:
            break
    # 將代號換回原關鍵字
    for idx, word in enumerate(keywords):
        text = text.replace('$"' + str(idx) + '"', word)

    """
    # 處理等號左式
    """
    text = text.replace("等於", "=")
    text = text.replace("逗號", ",")

    # 處理宣告的函數(左式)的縮寫: 如 fxy= -> f(x,y)= 、 f括號xy= -> f(x,y)=
    func_declare_match = re.search(r'^([a-zA-Z]\d*)(左?括號)?(([a-zA-Z]\d*)+)(右?括號)?=', text)
    if func_declare_match:
        args = re.split(r'(?=[a-zA-Z])', func_declare_match.groups()[2])[1:]
        text = func_declare_match.groups()[0] + '(' + ','.join(args) + ')=' + text[func_declare_match.end():]

    """
    # 常數
    """
    text = text.replace("圓周率", "PI")
    text = text.replace("PI", "(PI)")   # 先套好括號以免 P、I 被拆開
    text = text.replace("自然對數", "E")

    """
    # 敘述句裡給的括號 (主動括號)
    """
    text = text.replace("左括號", "(")
    text = text.replace("右括號", ")")
    # 處理括號簡稱
    text = text.replace("再括號", "(")
    text = text.replace("括號", "#")
    accu = 0
    for char in range(len(text)):
        if text[char] == '#':
            text = text[:char] + (')' if accu else '(') + text[char + 1:]
        if text[char] == '(':
            accu += 1
        elif text[char] == ')':
            accu -= 1
            if accu < 0:
                raise Exception("不合法括號")
    else:
        if accu:
            raise Exception("不合法括號")

    # --=----=----=----=----=----=----=----=----=----=----=----=----=----=----=----=----=----=----=-- #
    """
    # 以下皆為運算子的處理
    # 愈先套括號的運算子代表優先度愈高，運算元不會再被之後處理的運算子搶走，函數的括號則是可能整個被搶走故也要套括號
    # 主動括號:敘述句已有的括號(函數也算)，自動括號:本程式處理時套上的(函數也算)
    """

    # 不套括號代表運算元可以被之後的處理搶走，如 2*3**4 -> 2*(3**4)
    text = text.replace("加", "+")
    text = text.replace("減", "-")
    text = text.replace("負", "-")
    text = text.replace("乘以", "*")
    text = text.replace("乘", "*")
    text = text.replace("階*", "階乘")
    text = text.replace("除以", "/")
    text = text.replace("mod", "%")

    """
    # 處理取餘數(不套括號): 如 3對2取餘數 -> 3%2
    """
    while True:
        match = re.search(r'對(.+?)取餘數', text)
        if match:
            if re.fullmatch(r'\d+(\.\d+)?|[a-zA-Z]\d*', match.groups()[0]):     # 如果裡面只有一個數
                text = text[:match.start()] + '%' + match.groups()[0] + text[match.end():]
            else:
                text = text[:match.start()] + '%(' + match.groups()[0] + ')' + text[match.end():]
        else:
            break

    """
    # 處理次方: 如 2x13次方 -> 2x**13 、 2的x13次方 -> 2**x13 、 (x-1)(2*(1+3))次方 -> (x-1)**(2*(1+3))
    """
    text = text.replace("的平方", "的2次方")
    text = text.replace("平方", "的2次方")
    # 因此變數的要先處理，以免被當成數字，如 x13 被當成 13
    while True:
        match = re.search(r'的([a-zA-Z]\d*)次方', text)
        if match:
            text = text[:match.start()] + '_**_' + match.groups()[0] + text[match.end():]
        else:
            break
    while True:
        match = re.search(r'的?(\d+(\.\d+)?)次方', text)
        if match:
            text = text[:match.start()] + '_**_' + match.groups()[0] + text[match.end():]
        else:
            break
    while True:
        match = re.search(r'\)次方', text)
        if match:
            left, right = find_corresponding_bracket(match.start(), text), match.start()
            text = text[:left - (text[left - 1] == '的')] + '_**_' + text[left: right + 1] + text[match.end():]
        else:
            break
    # 套上括號: 將暫記的 _**_ 換成 ** ，如 (...)_**_(...) -> ((...)**(...)) ，若輸入是 ** 就不用管，因為也代表輸入者不要套
    while True:
        match = re.search(r'(\d+(\.\d+)?|[a-zA-Z]\d*|\))_\*\*_(\(|\d+(\.\d+)?|[a-zA-Z]\d*)', text)
        if match:
            start = find_corresponding_bracket(match.start(), text) if match.groups()[0] == ')' else match.start()
            end = find_corresponding_bracket(match.end() - 1, text) + 1 if match.groups()[2] == '(' else match.end()
            first = text[start: match.start() + 1] if match.groups()[0] == ')' else match.groups()[0]
            second = text[match.end() - 1: end] if match.groups()[2] == '(' else match.groups()[2]
            text = text[:start] + '(' + first + '**' + second + ')' + text[end:]
        else:
            break

    """
    # 處理階乘: 如 5階乘 -> factor(5)
    """
    text = text.replace('!', '階乘')
    # 若省略括號則補上，順便套上括號
    while True:
        match = re.search(r'(\d+(\.\d+)?|[a-zA-Z]\d*)階乘', text)
        if match:
            text = text[:match.start()] + '(factor(' + match.groups()[0] + '))' + text[match.end():]
        else:
            break
    # 沒省略括號的，順便套上括號
    while True:
        match = re.search(r'\)階乘', text)
        if match:
            left, right = find_corresponding_bracket(match.start(), text), match.start()
            text = text[:left] + '(factor(' + text[left+1:right] + '))' + text[match.end():]
        else:
            break

    """
    # 處理根號: 如 根號2 -> sqrt(2)
    """
    # 若省略括號則補上，順便套上括號
    while True:
        match = re.search(r'根號(\d+(\.\d+)?|[a-zA-Z]\d*)', text)
        if match:
            text = text[:match.start()] + '(sqrt(' + match.groups()[0] + '))' + text[match.end():]
        else:
            break
    # 沒省略括號的，順便套上括號
    while True:
        match = re.search(r'根號\(', text)
        if match:
            left, right = match.end()-1, find_corresponding_bracket(match.end()-1, text)
            text = text[:match.start()] + '(sqrt(' + text[left+1:right] + '))' + text[right+1:]
        else:
            break

    """
    # 處理三角函數:
    """
    text = text.replace("正弦", "sin")
    text = text.replace("餘弦", "cos")
    text = text.replace("正切", "tan")
    # 若省略括號則補上: 如 sinx -> sin(x)
    while True:
        match = re.search(r'(sin|cos|tan)((\d+(\.\d+)?)|[a-zA-Z]\d*)', text)
        if match:
            text = text[:match.start()] + match.groups()[0] + '(' + match.groups()[1] + ')' + text[match.end():]
        else:
            break
    # 套上括號
    text = text.replace("sin", "_sin_")
    text = text.replace("cos", "_cos_")
    text = text.replace("tan", "_tan_")
    while True:
        match = re.search(r'_(sin|cos|tan)_\(', text)
        if match:
            left, right = match.end()-1, find_corresponding_bracket(match.end()-1, text)
            text = text[:match.start()] + '(' + match.groups()[0] + '(' + text[left+1:right] + '))' + text[right+1:]
        else:
            break

    """
    # 處理對數:
    """
    # 處理給底的對數: 如 對數8以2為底 -> log(8, 2)
    while True:
        match = re.search(r'對數(.+)[以用](.+)作?為底數?', text)
        if match:
            text = text[:match.start()] + 'log(' + match.groups()[0] + ',' + match.groups()[1] + ')' \
                   + text[match.end():]
        else:
            break
    # 處理不給底的對數: 如 對數8 -> log(8)
    text = text.replace("對數", "log")
    # 若省略括號則補上:
    while True:
        match = re.search(r'log(\d+(\.\d+)?|[a-zA-Z]\d*)', text)
        if match:
            text = text[:match.start()] + 'log(' + match.groups()[0] + ')' + text[match.end():]
        else:
            break
    # 套上括號
    text = text.replace('log', '_log_')
    while True:
        match = re.search(r'_log_\(', text)
        if match:
            left, right = match.end()-1, find_corresponding_bracket(match.end()-1, text)
            text = text[:match.start()] + '(log(' + text[left+1:right] + '))' + text[right+1:]
        else:
            break

    """
    # 處理幾分之幾
    """
    while True:
        match = re.search(r'(\d+(\.\d+)?|[a-zA-Z]\d*|\))分之(\(|\d+(\.\d+)?|[a-zA-Z]\d*)', text)
        if match:
            start = find_corresponding_bracket(match.start(), text) if match.groups()[0] == ')' else match.start()
            end = find_corresponding_bracket(match.end() - 1, text) + 1 if match.groups()[2] == '(' else match.end()
            denominator = text[start: match.start() + 1] if match.groups()[0] == ')' else match.groups()[0]
            numerator = text[match.end() - 1: end] if match.groups()[2] == '(' else match.groups()[2]
            text = text[:start] + '(' + numerator + '/' + denominator + ')' + text[end:]
        else:
            break

    """
    # 處理微分: 如 (x**2)對x微分 -> diff(x**2, x)
    """
    while True:
        match = re.search(r'(\d+(\.\d+)?|[a-zA-Z]\d*)對(.+)做?微分', text)
        if match:
            text = text[:match.start()] + 'diff(' + match.groups()[0] + ',' + match.groups()[2] + ')' \
                   + text[match.end():]
        else:
            break
    while True:
        match = re.search(r'\)對(.+)做?微分', text)
        if match:
            left, right = find_corresponding_bracket(match.start(), text), match.start()
            text = text[:left] + 'diff(' + text[left + 1:right] + ',' + match.groups()[0] + ')' + text[match.end():]
        else:
            break
    # 套上括號
    text = text.replace('diff', '_diff_')
    while True:
        match = re.search(r'_diff_\(', text)
        if match:
            left, right = match.end()-1, find_corresponding_bracket(match.end()-1, text)
            text = text[:match.start()] + '(diff(' + text[left+1:right] + '))' + text[right+1:]
        else:
            break

    """
    # 處理定積分: 改為如 integrate(f,(x,a,b))
    """
    # 統一中文語法為: 對...從...到...做?定?積分
    while True:
        match = re.search(r'(從.+到.+)(對.+)做?定?積分', text)
        if match:
            text = text[:match.start()] + match.groups()[1] + match.groups()[0] + '做積分' + text[match.end():]
        else:
            break
    while True:
        match = re.search(r'(對.+)做?定?積分([a-zA-Z]\d*)?(從.+到(\d+(\.\d+)?|[a-zA-Z]\d*))', text)
        if match:
            text = text[:match.start()] + match.groups()[0] + match.groups()[2] + '做積分' + text[match.end():]
        else:
            break
    while True:
        match = re.search(r'(對.+)做?定?積分([a-zA-Z]\d*)?(從.+到)\(', text)
        if match:
            left, right = match.end() - 1, find_corresponding_bracket(match.end() - 1, text)
            text = text[:match.start()] + match.groups()[0] + match.groups()[2] + text[left:right + 1] + '做積分' \
                   + text[right + 1:]
        else:
            break
    # 再轉為 integrate(...)
    while True:
        match = re.search(r'(\d+(\.\d+)?|[a-zA-Z]\d*)對(.+)從(.+)到(.+?)做?定?積分', text)
        if match:
            text = text[:match.start()] + 'integrate(' + match.groups()[0] + ',(' + match.groups()[2] + ',' \
                   + match.groups()[3] + ',' + match.groups()[4] + '))' + text[match.end():]
        else:
            break
    while True:
        match = re.search(r'\)對(.+)從(.+)到(.+?)做?定?積分', text)
        if match:
            left, right = find_corresponding_bracket(match.start(), text), match.start()
            text = text[:left] + 'integrate(' + text[left + 1:right] + ',(' + match.groups()[0] + ',' \
                   + match.groups()[1] + ',' + match.groups()[2] + '))' + text[match.end():]
        else:
            break

    """
    # 處理不定積分: 改為如 integrate(f,x)
    """
    while True:
        match = re.search(r'(\d+(\.\d+)?|[a-zA-Z]\d*)對(.+)做?(不定)?積分', text)
        if match:
            text = text[:match.start()] + 'integrate(' + match.groups()[0] + ',' + match.groups()[2] + ')' \
                   + text[match.end():]
        else:
            break
    while True:
        match = re.search(r'\)對(.+)做?(不定)?積分', text)
        if match:
            left, right = find_corresponding_bracket(match.start(), text), match.start()
            text = text[:left] + 'integrate(' + text[left + 1:right] + ',' + match.groups()[0] + ')' + text[
                                                                                                       match.end():]
        else:
            break

    # 套上括號
    text = text.replace('integrate', '_integrate_')
    while True:
        match = re.search(r'_integrate_\(', text)
        if match:
            left, right = match.end()-1, find_corresponding_bracket(match.end()-1, text)
            text = text[:match.start()] + '(integrate(' + text[left+1:right] + '))' + text[right+1:]
        else:
            break

    """
    # 將省略參數的自訂函數補上括號及參數: 如 f -> f(x)
    """
    # 將關鍵字轉換成代號，避免如 diff 的 f 被當成自訂函數
    for idx, word in enumerate(keywords):
        text = text.replace(word, '$"' + str(idx) + '"')
    while True:     # 此 re.finditer 寫法和前面那些 re.search 寫法的差別在可以加條件，略過不符合條件的 match
        for match in re.finditer(r'[a-zA-Z]\d*(?!\()', text):   # 因為一樣需要重複搜尋，故也要設計好區別 pattern 是否未處理過
            func_name = match.group()
            if func_name in symbol and isinstance(symbol[func_name], sp.FunctionClass):
                text = text[:match.start()] + func_name + '(' + ','.join(symbol[func_name].args_name) + ')' \
                       + text[match.end():]
                break   # text 被修改就要跳出 iter 重新 find
        else:
            break
    # 將代號換回原關鍵字
    for idx, word in enumerate(keywords):
        text = text.replace('$"' + str(idx) + '"', word)

    """
    # 處理乘法縮寫: 如 ax -> a*x
    """
    constants = {'PI', 'E'}
    recipient = re.search(r'^([a-zA-Z]\d*)\([a-zA-Z]\d*(,[a-zA-Z]\d*)*\)=', text)
    keywords_functions = keywords - constants
    custom_functions = {func_name for func_name in symbol.keys() if isinstance(symbol[func_name], sp.FunctionClass)} | (
            {recipient.groups()[0]} if recipient else set())    # 包含即將定義的函式
    functions = list(keywords_functions)+list(custom_functions)     # 內建函數要先轉，不然像 diff 的 f 會被轉掉
    # 將非自訂變數轉換成代號，避免變 P*I、f*(x)
    for idx, word in enumerate(constants):
        text = text.replace(word, '$(' + str(idx) + ')')
    for idx, word in enumerate(functions):
        text = text.replace(word, '$"' + str(idx) + '"')
    # 補上省略掉的 * 號
    while True:
        match = re.search(r'(\d+(\.\d+)?|[a-zA-Z]\d*|\))([a-zA-Z]\d*|\(|\$)', text)
        if match:
            text = text[:match.start()] + match.groups()[0] + '*' + match.groups()[2] + text[match.end():]
        else:
            break
    # 將代號換回原字
    for idx, word in enumerate(constants):
        text = text.replace('$(' + str(idx) + ')', word)
    for idx, word in enumerate(functions):
        text = text.replace('$"' + str(idx) + '"', word)

    """
    # 將代號換回原指令
    """
    for idx, word in enumerate(instructions):
        text = text.replace('$<' + str(idx) + '>', word)

    return text


def register_callback_clear_history(callback):
    # 雖然可以從 mainUI 直接改 global，但用 setter 比較專業
    global callback_clear_history
    callback_clear_history = callback


def execute(std_input: str):
    """
    將標準敘述句作為運算式來執行運算或進行賦值
    """
    global symbol  # 所有變數與函數

    if std_input == 'reset_all':
        symbol = builtin_symbol
        callback_clear_history()    # callback to mainUI._clear_history
        return 'All reset'
    match = re.fullmatch(r'reset ([a-zA-Z]\d*)', std_input)
    if match:
        symbol[match.groups()[0]] = sp.Symbol(match.groups()[0])
        return match.groups()[0] + ' is reset'

    # 分成左右式，左式為函數右式為其函式，ex: f(x) 和 ax+b
    tokens = std_input.split('=')
    recipient = tokens[0] if len(tokens) == 2 else ""
    expr = tokens[1] if len(tokens) == 2 else tokens[0]

    # 宣告(右式)出現的未知數
    for variable in re.finditer(r'[a-zA-Z]\d*', expr):
        name = variable.group()
        if name not in symbol:
            symbol[name] = sp.Symbol(name)

    # print(symbol)
    # 計算 expr 作為輸出結果
    result = eval(expr, symbol)
    # print(symbol)     # 混入了奇怪的東西 wtf

    # if expr == 'f(x)':
    #     print(len(symbol))

    # 處理賦值給左式
    if recipient:
        func_declare_match = re.fullmatch(r'([a-zA-Z]\d*)\(([a-zA-Z]\d*(,[a-zA-Z]\d*)*)\)', recipient)
        expr_declare_match = re.fullmatch(r'([a-zA-Z]\d*)', recipient)
        # 宣告並定義函數
        if func_declare_match:
            func_name, func_args = func_declare_match.groups()[0], func_declare_match.groups()[1].split(',')
            # 自訂的 function 屬於 sp.FunctionClass 類，且每個自訂 function 本身都各自為一個類，類名為函數名
            func = sp.Function(func_name)

            func.args_name = tuple(func_args)   # 新宣告的 field
            # 將定義式的未知數替換為區域變數並記錄，如 f(x,y)=a*x+b*y+c 則 "a*x+b*y+c" -> "a*args[0]+b*args[1]+c"
            func.definition = expr   # 新宣告的 field
            for idx, arg in enumerate(func_args):
                func.definition = func.definition.replace(arg, 'args['+str(idx)+']')
            # call f(*args) 相當 call f.eval(*args)
            func.eval = lambda *args: eval(func.definition, symbol | {'args': args})  # Override
            # 嚴重 bug: 之前如果給過一樣的參數，就不會進來 eval()，尚未知道原因
            # 例 f(x) = ax，a=3，f(y)，a=5，再輸入 f(y) 還是得到 3y，沒有呼叫 eval() 重算。也不知道它從哪算出 3y 的

            symbol[func_name] = func    # 綁定
        # 宣告並設置運算式
        elif expr_declare_match:
            expr_name = expr_declare_match.groups()[0]
            symbol[expr_name] = result
        else:
            raise Exception("左式只能是一個函數格式或是一個變數格式")

    return str(result)


# class f(sp.Function):
#     @classmethod
#     def eval(cls, x):
#         return x + 3


if __name__ == "__main__":
    print(re.split(r'(?=[a-zA-Z])', 'x1y20zw4'))

    x = sp.Symbol('x')
    f = sp.Function('f')
    # f.args = 'x',
    f.eval = lambda *args: eval("2*args[0]+3", symbol | {'args': args})
    print(eval("f(2)", {'f': f}))
    print(isinstance(eval("f(2)", {'f': f}), sp.Number))

    # g = sp.Function('g')
    # g.args = 'x',
    # g.eval = lambda *args: eval("args[0]+2", symbol | {'args': args})
    # text = "f+g"
    # s = {'x': x, 'f': f, 'g': g}
    # # print(','.join(f.args))
    # while True:
    #     for match in re.finditer(r'[a-zA-Z]\d*(?!\()', text):
    #         if isinstance(s[match.group()], sp.FunctionClass):
    #             text = text[:match.start()] + match.group() + '(' + ','.join(s[match.group()].args) + ')' \
    #                    + text[match.end():]
    #             break
    #     else:
    #         break
    # print(text)
    # print(eval(text, s))
