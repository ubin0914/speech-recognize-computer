
"""
有繪圖功能的版本，但會被我的系統會擋下來
"""

import traceback
import tkinter as tk
from tkinter import messagebox
import threading
import matplotlib.pyplot as plt
import numpy as np
import random
from sympy.parsing.sympy_parser import parse_expr

from voice_io import *
from utils import *

now = 1
dic = {}


class Application(tk.Frame):

    def __init__(self, master, title="Speech Recognition Computer"):
        tk.Frame.__init__(self, master)

        self._input_history = []
        self._result_history = []
        register_callback_clear_history(self._clear_history)

        self.width = 800
        self.height = 150
        self._test_no = 0

        master.minsize(self.width, self.height)
        master.maxsize(self.width, self.height)
        master.title(title)
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        master.grid_rowconfigure(1, weight=1)
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", lambda: self.quit())

        # init widgets
        self.grid()
        self._init_widgets()

        # init global dic
        for i in range(ord('a'), ord('z') + 1):
            dic[chr(i)] = random.randint(1, 10)

        for i in range(ord('A'), ord('Z') + 1):
            dic[chr(i)] = random.randint(1, 10)

        dic['sin'] = np.sin
        dic['cos'] = np.cos
        dic['tan'] = np.tan
        dic['log'] = np.log
        dic['sqrt'] = np.sqrt

    def quit(self):
        self.master.destroy()
        print("quit")

    def _init_widgets(self):

        self._input_frame = tk.Frame()
        self._input_frame.grid(row=0, column=0, sticky="NSEW")
        self._input_frame.grid_columnconfigure(0, weight=1)
        self._input_frame.grid_rowconfigure(0, weight=1)

        self._result_frame = tk.Frame()
        self._result_frame.grid(row=1, column=0, sticky="NSEW")
        self._result_frame.grid_columnconfigure(0, weight=1)
        self._result_frame.grid_rowconfigure(0, weight=1)

        font_frame = ("Courier", 16)
        font_obj = ("Courier", 16)

        self._txtInput = tk.Entry(self._input_frame, font=font_obj)
        self._txtInput.grid(row=0, column=0, sticky="NSEW", padx=3, pady=3)

        self._imageOff = tk.PhotoImage(file="mic_off.png")
        self._imageOn = tk.PhotoImage(file="mic_on.png")
        self._btnMic = tk.Button(self._input_frame, width=35,
                                 command=lambda: threading.Thread(target=self._btnMic_press).start(),
                                 image=self._imageOff)
        self._btnMic.grid(row=0, column=1, sticky="NSEW", padx=3, pady=3)

        self._labelInput = tk.Label(self._input_frame, font=font_obj)
        self._labelInput.grid(row=1, column=0, sticky="W", padx=3, pady=3)
        self._imageLabel = tk.PhotoImage(file="label.png")
        self._His_frame_1 = None
        self._btnLabel = tk.Button(self._input_frame, width=35, image=self._imageLabel,
                                   command=self._btnHis_press)
        self._btnLabel.grid(row=1, column=1, sticky="NSEW", padx=3, pady=3)

        self._txtResult = tk.Entry(self._result_frame, font=font_obj, state="disabled")
        self._txtResult.grid(row=0, column=0, sticky="NSEW", padx=3, pady=3)
        self._imageResult = tk.PhotoImage(file="result.png")
        self._Graph_frame_1 = None
        self.ifG = None
        self._btnResult = tk.Button(self._result_frame, width=35, image=self._imageResult,
                                    command=self._btnGraph_press)
        self._btnResult.grid(row=0, column=1, sticky="NSEW", padx=3, pady=3)

    def _setInputText(self, input_text: str):
        self._txtInput.delete(0, "end")
        self._txtInput.insert(0, input_text)

    def _setInputLabel(self, input_text: str):
        self._labelInput.config(text="input: " + input_text)

    def _setResultText(self, result_text: str):
        self._txtResult.config(state="normal")
        self._txtResult.delete(0, "end")
        self._txtResult.insert(0, result_text)
        self._txtResult.config(state="disabled")

    def window_2(self):
        self._His_frame_1 = None
        self._His_frame.destroy()

    def _btnHis_press(self):
        if self._His_frame_1 == None:
            self._His_frame_1 = True
            self._His_frame = tk.Toplevel()
            self._His_frame.title('History')
            self._His_frame.geometry("340x200")
            self._His_frame.maxsize(width=340, height=200)
            self._His_frame.minsize(width=340, height=200)

            self._His_frame.protocol('WM_DELETE_WINDOW', self.window_2)

            self._His_frame.grid_rowconfigure(0, weight=1)
            self._His_frame.grid_columnconfigure(0, weight=1)

            self.inputLabel = tk.Label(self._His_frame, text="input")
            self.inputLabel.grid(row=0, column=0, sticky="NSEW", padx=3, pady=3)

            self.scrollbarInput = tk.Scrollbar(self._His_frame)
            self.scrollbarInput.grid(row=1, column=1, sticky="NS")
            self.listboxInput = tk.Listbox(self._His_frame)
            self.listboxInput.grid(row=1, column=0, sticky="NSEW", padx=3, pady=3)
            for i in self._input_history:
                self.listboxInput.insert(tk.END, i)
            self.listboxInput.config(yscrollcommand=self.scrollbarInput.set)
            self.scrollbarInput.config(command=self.listboxInput.yview)

            self.vertical1 = tk.Frame(self._His_frame, bg='gray', width=1)
            self.vertical1.grid(row=0, column=2, sticky="NS", padx=1)
            self.vertical2 = tk.Frame(self._His_frame, bg='gray', width=1)
            self.vertical2.grid(row=1, column=2, sticky="NS", padx=1)

            self.resultLabel = tk.Label(self._His_frame, text="result")
            self.resultLabel.grid(row=0, column=3, sticky="NSEW", padx=3, pady=3)

            self.scrollbarResult = tk.Scrollbar(self._His_frame)
            self.scrollbarResult.grid(row=1, column=4, sticky="NS")
            self.listboxResult = tk.Listbox(self._His_frame)
            self.listboxResult.grid(row=1, column=3, sticky="NSEW", padx=3, pady=3)
            for i in self._result_history:
                self.listboxResult.insert(tk.END, i)
            self.listboxResult.config(yscrollcommand=self.scrollbarResult.set)
            self.scrollbarResult.config(command=self.listboxResult.yview)

            self._His_frame.mainloop()
        else:
            tk.messagebox.showwarning(title='警告', message='不可以創建兩個子窗口！')

    def _His_refresh(self):
        if self._His_frame_1 == True:
            self.listboxInput.delete(0, tk.END)
            for i in self._input_history:
                self.listboxInput.insert(tk.END, i)

            self.listboxResult.delete(0, tk.END)
            for i in self._result_history:
                self.listboxResult.insert(tk.END, i)
        else:
            return

    def Graphwindow_2(self):
        self._Graph_frame_1 = None
        self._Graph_frame.destroy()

    def _btnGraph_press(self):

        if self.ifG == None:
            tk.messagebox.showwarning(title='警告', message='沒有結果！')
            return

        if self._Graph_frame_1 == None:
            self._Graph_frame_1 = True
            self._Graph_frame = tk.Toplevel()

            self._Graph_frame.protocol('WM_DELETE_WINDOW', self.Graphwindow_2)
            self._Graph_frame.title('Graph')
            self._Graph_frame.geometry("600x500")
            self._Graph_frame.grid_rowconfigure(0, weight=1)
            self._Graph_frame.grid_columnconfigure(0, weight=1)

            self._Graph_frame.maxsize(width=600, height=500)
            self._Graph_frame.minsize(width=600, height=500)
            nowgraph = now-1
            nowgraphway = str(nowgraph)+".png"

            self._imageGraph = tk.PhotoImage(file=nowgraphway)
            self.resultGraph = tk.Label(self._Graph_frame, image= self._imageGraph)
            self.resultGraph.grid(row=0, column=0, sticky="NSEW", padx=3, pady=3)

            self._Graph_frame.mainloop()
        else:
            tk.messagebox.showwarning(title='警告', message='不可以創建兩個子窗口！')

    def _Graph_refresh(self):
        result_text = self._result_text
        self._plotting(result_text)
        if self._Graph_frame_1 == True:
            nowgraph = now-1
            nowgraphway = str(nowgraph)+".png"

            self._imageGraph = tk.PhotoImage(file=nowgraphway)
            self.resultGraph.config(image=self._imageGraph)
        else:
            return

    # 以上 @juruo44855 你管
    # --=----=----=----=----=----=----=----=----=----=----=----=----=----=----=----=----=----=----=----=-- #

    def _btnMic_press(self):
        self._btnMic.config(state="disabled", image=self._imageOn)

        # 開啟這三行改為測試自訂輸入
        # self._use_test_texts()
        # self._btnMic.config(state="normal", image=self._imageOff)
        # return

        print("--=----=----=----=----=----=----=----=----=----=----=----=----=--")
        print("listening...")
        # 連線 google 語音辨識
        heard_texts = listen()
        if not heard_texts:
            speak("無法辨識 請崇試")
            self._btnMic.config(image=self._imageOff)
            return
        else:
            pass  # speak(heard_texts['alternative'][0]['transcript'])
        confidence = heard_texts['alternative'][0]['confidence']
        # listen() 回傳的型態原本長這樣，先將所有句子攤成 list
        heard_texts = [item['transcript'] for item in heard_texts['alternative']]

        # 有指令的敘述優先，其次依原本的排序
        heard_texts.sort(key=lambda text: has_instruction(text), reverse=True)
        print("heard texts:", heard_texts, " first confidence:", confidence)

        first_text, first_standard_input, first_text_errorInfo = "", "", ""
        # 嘗試每個聽到的可能敘述
        for idx, input_text in enumerate(heard_texts):
            # 先校正選字錯誤
            input_text = word_correction(input_text)

            standard_input = ""
            try:
                # 將口述的自然敘述句翻譯為標準敘述句
                standard_input = translate_to_standard(input_text)
                # 照標準敘述句執行並計算結果
                result_text = execute(standard_input)
            except:
                # 翻譯或執行期間發生錯誤，代表語法不正確，再換下一個聽到的敘述
                if not first_text_errorInfo:  # 將聽到的第一句(最可能的)的錯誤資訊記錄下來
                    first_text = input_text
                    first_standard_input = standard_input
                    first_text_errorInfo = traceback.format_exc()
                continue
            # 語法正確且執行完畢
            self._setInputText(input_text)
            self._setInputLabel(standard_input)
            self._result_text = result_text
            if standard_input != 'reset_all':
                self._input_history.append(standard_input)
                self._result_history.append(result_text)
                self._His_refresh()  # 刷新歷史紀錄
                self._Graph_refresh()  # 刷新圖片紀錄
            print("Match in", idx + 1, "\bth text.")
            print("standard input:", standard_input)
            # 成功便不用再試下一個
            break
        # 每個聽到的可能敘述的語法都錯誤
        else:
            self._setInputText(first_text)
            print("All possible texts are wrong expression.")
            speak("語法錯誤，請崇試")

        # 若第一句語法錯誤就顯示其錯誤資訊，不代表每一句都失敗
        if first_text_errorInfo:
            print("-- Error information of first text --")
            print("first standard input:", first_standard_input)
            print(first_text_errorInfo)

        self._btnMic.config(state="normal", image=self._imageOff)

    def _use_test_texts(self):
        # 自訂測資
        # input_texts = ["f1(x)等於2x3次方加3x平方減5x減8", "f2(x)等於f1對x微分", "f1", "f2"]
        # input_texts = ["括號x-1括號括號2左括號1+3括號括號次方", "2x13次方", "2的x13次方", "正弦x2次方分之一", "(x分之1)對x積分"]
        # input_texts = ["正弦x2次方"]
        # input_texts = ["根號x乘y"]
        # input_texts = ["(x三次方)對x積分從0到(1+1)"]
        # input_texts = ["f(x)=ax**2+bx", "a=3x", "g(x)=f對x微分", "f", "a"]
        # input_texts = ["f(x,y)等於ax3次方加bxy減y的n次方", "f對x微分", "f對y微分"]
        input_texts = ["f(x)=2x+3", "g(x)=x+2", "f+g", "f(4)", "f(t-1)", "重設全部", "f(t-1)"]
        # input_texts = ["f1括號xy=2x+y", "f2xy=x-2y", "g左括號xy右括號=f1+f2", "g(2,1)", "f1(1,2)+f2"]
        # input_texts = ["根號二分之一", "4分之對數27以3為底", "3分之正弦括號2分之圓周率括號"]
        # input_texts = ["a=3", "ax+b", "重設未知數a", "ax+b"]

        if self._test_no == len(input_texts):
            return
        input_text = input_texts[self._test_no]
        self._test_no += 1

        self._setInputText(input_text)
        try:
            standard_input = translate_to_standard(input_text)
        except:
            print(traceback.format_exc())
            speak("翻譯錯誤")
            return
        self._setInputLabel(standard_input)
        print("standard input:", standard_input)
        try:
            result_text = execute(standard_input)
        except:
            print(traceback.format_exc())
            speak("執行錯誤")
            return
        self._setResultText(result_text)
        self._result_text = result_text
        if standard_input != 'reset_all':
            self._input_history.append(standard_input)
            self._result_history.append(result_text)
            self._His_refresh()  # 刷新歷史紀錄
            self._Graph_refresh()  # 刷新圖片紀錄

    def _clear_history(self):
        self._input_history = []
        self._result_history = []
        self._His_refresh()  # 刷新歷史紀錄

    # --=----=----=----=----=----=----=----=----=----=----=----=----=----=----=----=----=----=----=----=-- #
    # 以下 @leo_yu @夜黑鷹 你們管

    def _print_result(self, result_text: str):
        # --=----=----=----=----=----=----=----=----=----=----=----=--
        #
        #                           外包
        #
        # --=----=----=----=----=----=----=----=----=----=----=----=--
        pass

    def _plotting(self, equation: str):
        self.ifG = True
        global now, dic
        xmin, xmax = -500, 500
        print(equation)

        try:
            val = parse_expr(equation)
            variable = range(xmin, xmax)
            variable_name = 'x'
            ans = [val for _ in variable]
            plt.plot(variable, ans, label=equation)
            plt.grid(True)
            plt.xlabel(variable_name)
            plt.ylabel(f'f({variable_name})')
            equation = equation.replace('**', '^')
            equation = equation.replace('pi', 'π')
            plt.title(equation)
            plt.legend()
            plt.savefig(f'{now}.png')
            now += 1
        except:
            try:
                variable = np.linspace(xmin, xmax, 10000)
                variable_name = ""
                if equation.find('x'):
                    dic['x'] = variable
                    variable_name = 'x'
                else:
                    for i in equation:
                        if 'a' <= i <= 'z' or 'A' <= i <= 'Z':
                            dic[i] = variable
                            variable_name = i
                            break
                # print(dic)
                ans = eval(equation, dic)
                print(ans)
                plt.plot(variable, ans, label=equation)
                plt.grid(True)
                plt.xlabel(variable_name)
                plt.ylabel(f'f({variable_name})')
                equation = equation.replace('**', '^')
                equation = equation.replace('pi', 'π')
                plt.xlim(-10, 10)
                plt.ylim(-10, 10)
                title = ""
                sk = 0
                for i in range(len(equation)):
                    if sk:
                        sk -= 1
                        continue
                    if equation[i] == 's' and equation[i + 1] == 'q':
                        title += 'sqrt'
                        sk += 3
                    elif (equation[i] == 's' and equation[i + 1] == 'i') or \
                        (equation[i] == 'c' and equation[i + 1] == 'o') or \
                        (equation[i] == 't' and equation[i + 1] == 'a') or \
                        (equation[i] == 'l' and equation[i + 1] == 'o'):
                        title += "".join(equation[j] for j in range(i, i + 3))
                        sk += 2
                    else:
                        if equation[i].isalpha() and equation[i] != variable_name:
                            title += str(dic[equation[i]])
                        else:
                            title += equation[i]
                plt.title(title)
                plt.legend()
                plt.savefig(f'{now}.png')
                now += 1
            except:
                pass


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
