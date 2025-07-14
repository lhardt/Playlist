import tkinter as tk
import tkinter.ttk as ttk
import threading
import subprocess
import os
import json

class App(tk.Tk): 

    def add_input(self, frame, label_text, input, row, paddings):
        label = ttk.Label(frame, text=label_text)
        label.grid(column=0, row=row, sticky="E", **paddings)
        input.grid(column=1, row=row, sticky="WE", **paddings)


    def print(self, text):
        self.output_widget.insert('end', "\n")
        self.output_widget.insert('end', text)

    def clear(self, event=None):
        self.output_widget.delete('0.0', tk.END)

    def recompose_filename(self, *args):
        filename = self.artist_var.get() + " - " + self.name_var.get()
        self.filename_var.set(filename)
        pass

    def update_info_file(self, info_filename,name,artist,album,filename):
        info = {}
        with open(info_filename, 'r') as file:
            info = json.load(file)
        
        info['artist'] = artist
        info['album'] = album
        info['track'] = name


        with open(info_filename, 'w') as file:
            json.dump(info, file)

    def donwload_multithread(self):
        thread = threading.Thread(target=self.download)
        thread.start()

    def download(self, event=None):
        self.print(f"Tentando baixar a música {self.name_var.get()}!" )
        
        url = self.url_var.get().strip()
        name = self.name_var.get().strip()
        artist = self.artist_var.get().strip()
        album = self.album_var.get().strip()
        filename = self.filename_var.get().strip()


        download_info_args = ["python", "-m", "yt_dlp",  "--audio-format", "mp3",
                              "--audio-quality", "320k", "--extract-audio", 
                              "--embed-thumbnail", "--embed-metadata", "--embed-subs",
                "--add-metadata" ,
                "--write-info-json", "--skip-download", url, '-f', 'bestaudio']
       
        self.print("Baixando dados do vídeo!")
        
        result = subprocess.run(download_info_args, 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
        
        self.print(result.stdout.decode("utf-8"))
        self.print(result.stderr.decode("utf-8"))
        
        result_str = result.stdout.decode("utf-8")

        info_filename = result_str[  
                result_str.find("Writing video metadata as JSON to: ") + len("Writing video metadata as JSON to: ") :
                result_str.find(".info.json") + len(".info.json") 
        ]

        self.print(f"Info File  Must be :  <<{info_filename}>> ")

        if( len(info_filename) == 0):
            self.print("Erro...?")
            return


        self.update_info_file(info_filename,name,artist,album,filename)

        args = ["python", "-m", "yt_dlp", 
                # "-f" "\"bestaudio\""

                "--audio-format", "mp3",

                "--extract-audio", 

                "--no-write-info-json", "--load-info-json", info_filename,
                
                "--embed-metadata",
                #"--embed-subs",

                # "--embed-info-json", 

                #"--embed-thumbnail","--convert-thumbnails", "png", 

                #"--print", "filename",

                "-o", filename,
                ]

        self.print("Baixando o vídeo!")
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
        self.print(result.stdout)
        self.print(result.stderr)
        
        self.print(f"---- Finalizado:  {filename} -----")

    def __init__(self):
        super().__init__()
    
        self.title("Nosso Downloader!")
        self.resizable()

        paddings_outer = {'padx': 10, 'pady': 10}
        paddings = {'padx': 0, 'pady': 5}

        ttk.Label(self, text="Nosso downloader, princesa!").pack(**paddings_outer, anchor="center")

        # root.configure(background="yellow")
        # root.minsize(300, 300)
        # root.maxsize(500, 500)
        # root.geometry("300x300+50+50")
        frame = tk.Frame(self, **paddings_outer)
        frame.pack(fill='x')
    
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=3)


        self.folder_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.album_var = tk.StringVar()
        self.artist_var = tk.StringVar()
        self.filename_var = tk.StringVar()

        self.name_var.trace_add('write',self.recompose_filename)
        self.artist_var.trace_add('write',self.recompose_filename)

        self.folder_var.set(os.getcwd())

        self.add_input(frame, "Pasta:", ttk.Entry(frame, textvariable=self.folder_var ), 0, paddings)
        self.add_input(frame, "URL do Youtube:", ttk.Entry(frame, textvariable=self.url_var ), 1, paddings)
        self.add_input(frame, "Nome da Música:", ttk.Entry(frame, textvariable=self.name_var ), 2, paddings)
        self.add_input(frame, "Nome do Artista:", ttk.Entry(frame, textvariable=self.artist_var ), 3, paddings)
        self.add_input(frame, "Nome do Álbum:", ttk.Entry(frame, textvariable=self.album_var ), 4, paddings)
        self.add_input(frame, "Nome do Arquivo:", ttk.Entry(frame, textvariable=self.filename_var ), 5, paddings)
    
    
        go_button = ttk.Button(self, text="Baixar! (Ctrl-Enter)", command=self.donwload_multithread)
        go_button.pack(fill='x', **paddings_outer)
        self.bind("<F1>", self.download)
    
        progress_bar = ttk.Progressbar(self, mode="determinate")
        progress_bar.pack(fill='x', **paddings_outer)
    
        output_widget = tk.Text(self, width=50, height=20, wrap='none', )
        output_widget.pack(padx=10, pady=10, fill='x')
        self.output_widget = output_widget

        go_button = ttk.Button(self, text="Limpar texto (F2)", command=self.clear)
        go_button.pack(fill='x', **paddings_outer)
        self.bind("<F2>", self.clear)

def main():
    root = App()
    root.mainloop()

if __name__ == '__main__':
    main()

