import tkinter as tk
import tkinter.ttk as ttk
import threading
import tkinter.filedialog as fdialog
import urllib.parse
import subprocess
import webbrowser
import os
import json




class App(tk.Tk): 

    def add_input(self, frame, label_text, input, row, paddings):
        label = ttk.Label(frame, text=label_text)

        label.grid(column=0, row=row, sticky="E", **paddings)
        input.grid(column=1, row=row, sticky="WE", **paddings)

    def set_context_title(self, title):
        partial_title = "Nosso Downloader"

        if self.usinglist_var.get() :
            partial_title = partial_title + " - " + self.filename_var.get()

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


        download_info_args = ["python", "-m", "yt_dlp",  "--audio-format", "mp3",
                              "--audio-quality", "320k", "--extract-audio",
                              '-o', 'fileinfothing',
                              "--embed-thumbnail", "--embed-metadata", "--embed-subs",
                "--add-metadata" ,
                "--write-info-json", "--skip-download", url, '-f', 'bestaudio']
       
        self.print("Baixando dados do vídeo!")
        
        result = subprocess.run(download_info_args, 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
        
        self.print(result.stdout.decode("cp1252"))
        self.print(result.stderr.decode("cp1252"))
        
        result_str = result.stdout.decode("cp1252")

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

                "--embed-thumbnail","--convert-thumbnails", "png", 

                #"--print", "filename",

                "-o", filename,
                ]

        self.print("Baixando o vídeo!")
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,shell=True)
        self.print(result.stdout)
        self.print(result.stderr)
        
        self.print(f"---- Finalizado:  {filename} -----")
        self.set_context_title("")

        self.set_next_item_from_list()

    def set_next_item_index_to_download(self,list_items):

        i = 0

        previous_i = self.current_list_item_index
        if previous_i == None:
            previous_i = -1

        for item in list_items:
            if ('downloaded' not in item) and ( i > previous_i ) :
              self.current_list_item_index = i
              return i
            i += 1

        self.current_list_item_index = None
        return None

    def mark_current_item_as_downloaded(self):
        if self.current_list_item_index is not None:
            list_data = []
            
            # Read
            with open( self.listfilename_var.get() , 'r', encoding='utf-8' ) as current_listfile:
                list_data = json.load(current_listfile)

            list_data[self.current_list_item_index]['link'] = self.url_var.get()
            list_data[self.current_list_item_index]['downloaded'] = True


            # Save
            with open( self.listfilename_var.get() , 'w', encoding='utf-8' ) as current_listfile:
                json.dump(list_data,current_listfile)


    def set_next_item_from_list(self):
        self.mark_current_item_as_downloaded()

        if self.usinglist_var.get() is True:

            list_data = []
            with open( self.listfilename_var.get() , 'r', encoding='utf-8' ) as current_listfile:
                list_data = json.load(current_listfile)

            self.set_next_item_index_to_download(list_data)

            list_item = list_data[ self.current_list_item_index ]

            self.artist_var.set( list_item['artists'] )
            self.name_var.set( list_item['title'] )
            self.album_var.set( list_item['album'] )
            self.url_var.set( "" )

            self.print(f"Editando agora arquivo \"{ list_item['title'] }\" ")

    def on_usinglist_change(self):
        if self.usinglist_var.get() :
            #self.usinglist_var.set(False)
            file = fdialog.askopenfile( initialdir= os.getcwd() )
            if file is None:
                self.usinglist_var.set(False)
                self.current_list_item_index = None
            else:
                self.listfilename_var.set(str(file.name))
                file.close()

                #self.songname_entry.configure(state=tk.DISABLED)
                #self.album_entry.configure(state=tk.DISABLED)
                #self.artist_entry.configure(state=tk.DISABLED)

                self.set_next_item_from_list()

        else:
            # can jeopardize save process self.listfilename_var.set("")
            self.songname_entry.configure(state=tk.NORMAL)
            self.album_entry.configure(state=tk.NORMAL)
            self.artist_entry.configure(state=tk.NORMAL)

            #self.usinglist_var.set(True)

    def on_listfilename_change(self, *args):
        self.listfile_checkbox.configure(text= self.listfilename_var.get())

    def __init__(self):
        super().__init__()

        self.list_filename = None
        self.current_list_item_index = None

        self.title("Nosso Downloader!")
        self.resizable()

        small_paddings = {'padx': 10, 'pady': 10}
        paddings_outer = {'padx': 10, 'pady': 10}
        paddings = {'padx': 0, 'pady': 5}

        outer_pane = tk.Frame(self)
        outer_pane.pack(expand=True, fill='x', **small_paddings)
        
        left_frame = tk.LabelFrame(outer_pane, text="Nosso Conversor, gatinha!", **paddings_outer)
        left_frame.pack(fill='x', expand=True, side="left")

        right_frame = tk.LabelFrame(outer_pane, text="Mensagens:", **paddings_outer)
        right_frame.pack(side="right", fill="y")

        self.footer_image = tk.PhotoImage( file = os.getcwd() +  "\\cat.png")

        self.footer_label = tk.Label(left_frame, image=self.footer_image)
        self.footer_label.photo = self.footer_image
        
        frame = tk.Frame(left_frame)

        frame.pack(fill='x')
    
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=3)


        self.folder_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.album_var = tk.StringVar()
        self.artist_var = tk.StringVar()
        self.filename_var = tk.StringVar()
        self.usinglist_var = tk.BooleanVar()
        self.listfilename_var = tk.StringVar()
        self.describing_var = tk.StringVar()
        
        #ttk.Label(self, textvariable=self.describing_var).pack(**paddings_outer, anchor="center")

        self.listfile_checkbox = ttk.Checkbutton(frame, variable=self.usinglist_var, command=self.on_usinglist_change)

        self.listfilename_var.trace_add('write', self.on_listfilename_change)
        self.name_var.trace_add('write',self.recompose_filename)
        self.artist_var.trace_add('write',self.recompose_filename)

        self.folder_var.set(os.getcwd())

        self.folder_entry = ttk.Entry(frame, textvariable=self.folder_var )
        self.url_entry = ttk.Entry(frame, textvariable=self.url_var )
        self.songname_entry = ttk.Entry(frame, textvariable=self.name_var )
        self.artist_entry = ttk.Entry(frame, textvariable=self.artist_var )
        self.album_entry = ttk.Entry(frame, textvariable=self.album_var )

        self.add_input(frame, "Usando uma Lista:", self.listfile_checkbox, 0, paddings)
        self.add_input(frame, "Pasta:", self.folder_entry, 1, paddings)
        self.add_input(frame, "URL do Youtube:", self.url_entry, 2, paddings)
        self.add_input(frame, "Nome da Música:", self.songname_entry, 3, paddings)
        self.add_input(frame, "Nome do Artista:", self.artist_entry, 4, paddings)
        self.add_input(frame, "Nome do Álbum:", self.album_entry, 5, paddings)
        self.add_input(frame, "Nome do Arquivo:", ttk.Entry(frame, textvariable=self.filename_var ), 6, paddings)
    
    
        self.youtube_link = tk.Label(self, fg="blue", cursor="hand2")
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

