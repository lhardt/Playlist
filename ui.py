import tkinter as tk
import ttkbootstrap as ttk
import threading
import tkinter.filedialog as fdialog
import urllib.parse
import subprocess
import webbrowser
import os
import json
import sys


DEFAULT_THEME = 'solarized-light'

class App(ttk.App):

    def switch_theme(self):
        theme_name = self.theme_dropdown.get()
        self.theme_use(theme_name)

    def add_input(self, frame, label_text, input, row, paddings):
        label = ttk.Label(frame, text=label_text)

        label.grid(column=0, row=row, sticky="E", **paddings)
        input.grid(column=1, row=row, sticky="WE", **paddings)

    def set_context_title(self, title):
        partial_title = "Nosso Downloader"

        if title is not None and title != '':
            partial_title = partial_title + " - " + title

        self.title(partial_title)

    def print(self, text):
        self.output_widget.insert('end', "\n")
        self.output_widget.insert('end', text)
        self.output_widget.yview(tk.END)

    def clear(self, event=None):
        self.output_widget.delete('0.0', tk.END)
    
    def on_click_youtube_link(self, *args):
        url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(self.filename_var.get())
        webbrowser.open_new(url)


    def recompose_filename(self, *args):
        filename = self.artist_var.get() + " - " + self.name_var.get()
        self.filename_var.set(filename)
        self.youtube_link.configure(text=f"Pesquisar\"{filename}\" no Youtube")
        self.set_context_title("")
        pass

    def update_info_file(self, info_filename,name,artist,album,filename):
        info = {}
        with open(info_filename, 'r', encoding="utf-8") as file:
            info = json.load(file)

        info['artist'] = artist
        info['album'] = album
        info['track'] = name


        with open(info_filename, 'w', encoding='utf-8') as file:
            json.dump(info, file)

    def donwload_multithread(self):
        thread = threading.Thread(target=self.download)
        thread.start()


    def download(self, event=None):
        self.print(f"Tentando baixar a música {self.name_var.get()}!" )
        self.set_context_title(f"Baixando {self.name_var.get()}!")
        url = self.url_var.get().strip()
        name = self.name_var.get().strip()
        artist = self.artist_var.get().strip()
        album = self.album_var.get().strip()
        filename = self.filename_var.get().strip()

        if url.find("&") > 0 :
            url = url[ 0 :  url.find("&") ]

        self.url_var.set(url)

        if url is None or url == "":
            self.print("URL em branco!")
            return

        if name is None or name == "":
            self.print("Nome da música em branco!")
            return
        
        if filename is None or filename == "":
            self.print("Nome do arquivo em branco!")
            return


        download_info_args = [sys.executable, "-m", "yt_dlp",  "--audio-format", "mp3",
                              "--audio-quality", "320k", "--extract-audio",
                              '-o', 'fileinfothing',
                              "--embed-thumbnail", "--embed-metadata", "--embed-subs",
                "--add-metadata" ,
                "--write-info-json", "--skip-download", url, '-f', 'bestaudio']
       
        self.print("Baixando dados do vídeo!")
        
        result = subprocess.run(download_info_args, 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        self.print(result.stdout.decode("utf8"))
        self.print(result.stderr.decode("utf8"))
        
        result_str = result.stdout.decode("utf8")

        info_filename = result_str[  
                result_str.find("Writing video metadata as JSON to: ") + len("Writing video metadata as JSON to: ") :
                result_str.find(".info.json") + len(".info.json") 
        ]

        self.print(f"Info File  Must be :  <<{info_filename}>> ")

        if( len(info_filename) == 0):
            self.print("Erro...?")
            return


        self.update_info_file(info_filename,name,artist,album,filename)

        args = [sys.executable, "-m", "yt_dlp", 
                # "-f" "\"bestaudio\""

                "--audio-format", "mp3",

                "--extract-audio", 

                "--no-write-info-json", "--load-info-json", info_filename,

                "--embed-metadata",
                #"--embed-subs",

                # "--embed-info-json", 

                "--embed-thumbnail","--convert-thumbnails", "png", 

                #"--print", "filename",

                "-o", filename,
                ]

        self.print("Baixando o vídeo!")
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.print(result.stdout)
        self.print(result.stderr)
        
        self.print(f"---- Finalizado:  {filename} -----")
        self.set_context_title("")

    def __init__(self, theme=DEFAULT_THEME):
        super().__init__(theme=theme)

        self.list_filename = None
        self.current_list_item_index = None

        self.title("Nosso Downloader!")
        self.resizable()

        small_paddings = {'padx': 10, 'pady': 10}
        paddings_outer = {'padx': 10, 'pady': 10}
        padding_outer = 10
        paddings = {'padx': 0, 'pady': 5}

        outer_pane = tk.Frame(self)
        outer_pane.pack(expand=True, fill='x', **small_paddings)
        
        left_frame = ttk.LabelFrame(outer_pane, text="Nosso Conversor, gatinha!", padding=padding_outer)
        left_frame.pack(fill='x', expand=True, side="left")

        right_frame = ttk.LabelFrame(outer_pane, text="Mensagens:", padding=padding_outer)
        right_frame.pack(side="right", fill="y")

        self.footer_image = tk.PhotoImage( file = os.getcwd() + os.sep +  "cat.png")

        self.footer_label = ttk.Label(left_frame, image=self.footer_image)
        self.footer_label.photo = self.footer_image
        
        frame = ttk.Frame(left_frame)

        frame.pack(fill='x')
    
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=3)


        self.folder_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.album_var = tk.StringVar()
        self.artist_var = tk.StringVar()
        self.filename_var = tk.StringVar()
        self.listfilename_var = tk.StringVar()
        self.describing_var = tk.StringVar()

        self.name_var.trace_add('write',self.recompose_filename)
        self.artist_var.trace_add('write',self.recompose_filename)

        self.folder_var.set(os.getcwd())

        self.folder_entry = ttk.Entry(frame, textvariable=self.folder_var )
        self.url_entry = ttk.Entry(frame, textvariable=self.url_var )
        self.songname_entry = ttk.Entry(frame, textvariable=self.name_var )
        self.artist_entry = ttk.Entry(frame, textvariable=self.artist_var )
        self.album_entry = ttk.Entry(frame, textvariable=self.album_var )
        self.theme_dropdown = ttk.Combobox(frame, values=ttk.Style().theme_names(), state="readonly")

        app = self
        #theme_dropdown.pack(padx=10, pady=0, fill='x' , expand=True)
        self.theme_dropdown.bind("<<ComboboxSelected>>", lambda _ : app.switch_theme())
        #self.theme_dropdown = theme_dropdown

        self.add_input(frame, "Tema:", self.theme_dropdown, 1, paddings)
        self.add_input(frame, "Pasta:", self.folder_entry, 2, paddings)
        self.add_input(frame, "URL do Youtube:", self.url_entry, 3, paddings)
        self.add_input(frame, "Nome da Música:", self.songname_entry, 4, paddings)
        self.add_input(frame, "Nome do Artista:", self.artist_entry, 5, paddings)
        self.add_input(frame, "Nome do Álbum:", self.album_entry, 6, paddings)
        self.add_input(frame, "Nome do Arquivo:", ttk.Entry(frame, textvariable=self.filename_var ), 7, paddings)

        self.youtube_link = ttk.Label(self, foreground="blue", cursor="hand2")
        self.youtube_link.pack(anchor='center' ,**paddings_outer)
        self.youtube_link.bind("<Button-1>", self.on_click_youtube_link)

        go_button = ttk.Button(left_frame, text="Baixar! (F1)", command=self.donwload_multithread)
        go_button.pack(fill='x', **paddings_outer)
        self.bind("<F1>", self.download)
    
        #progress_bar = ttk.Progressbar(self, mode="determinate")
        #progress_bar.pack(fill='x', **paddings_outer)
    
        output_widget = tk.Text(right_frame, width=50, height=20, wrap='none', )
        output_widget.pack(padx=10, pady=10, fill='y' , expand=True)
        self.output_widget = output_widget

        go_button = ttk.Button(right_frame, text="Limpar texto (F2)", command=self.clear)
        go_button.pack(fill='x', **paddings_outer)


        self.bind("<F2>", self.clear)

        self.footer_label.pack(anchor="center")

def main():
    root = App()
    root.mainloop()

if __name__ == '__main__':
    main()

