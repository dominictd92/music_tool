import os
from pathlib import Path
from os import mkdir, listdir, replace, rename
from os.path import isfile, join, isdir, basename

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from mutagen import MutagenError
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3


# remove any colons and slashes from text to use for folder names
def make_file_folder_safe_string(replacer_string: str = ""):
    if isinstance(replacer_string, str):
        replacer_string = replacer_string.replace(":", "-").replace("/", "&")
    else:
        print(type(replacer_string))
    return replacer_string


# recursive method that gets all files within a directory given any
def get_list(list_of_songs: list, directory: str, extensions: tuple = ("", ""), sub_dir: bool = True):
    for temp_dir in listdir(directory):
        joined_directory = join(directory, temp_dir)
        if isdir(joined_directory) and sub_dir:
            list_of_songs.extend(get_list([], joined_directory, extensions))
        elif isfile(joined_directory) and joined_directory.endswith(extensions):
            list_of_songs.append(joined_directory)
    return list_of_songs


# recursive method that gets all mp3 files within a directory
def get_mp3_list(list_of_songs: list, directory: str):
    # forced tuple so NONE is a placeholder for a false extension
    return get_list(list_of_songs, directory, ('.mp3', 'NONE'))


# recursive method that gets all mp4 and m4a files within a directory
def get_mp4_list(list_of_songs: list, directory: str):
    return get_list(list_of_songs, directory, extensions=('.mp4', '.m4a'))


# move a list of files from one destination to another with no exceptions
def move_files(destination: str = None, source: str = None, list_of_files: list = None):
    if destination is not None and source is not None:
        if isdir(destination) and isdir(source):
            if list_of_files is not None:
                for file in list_of_files:
                    file_name = basename(file)

                    os.replace(file, join(destination, file_name))
        else:
            messagebox.showerror("Move Error", "Destination or Source was not valid.")
    else:
        messagebox.showerror("Move Error", "Destination or Source was empty.")


# method to move music files from one location to another while organizing them by artist and album
def organize_files(source: str, destination: str):
    if isdir(source) and isdir(destination):
        music_files = get_list([], source)
        for file in music_files:
            file_name = os.path.basename(file)
            temp_destination: str = destination
            try:
                music_file = MP3(file, ID3=EasyID3)

                if music_file["artist"] is not None:
                    # if there is no artist folder, create one
                    artist = make_file_folder_safe_string(music_file["artist"])
                    if not isdir(join(temp_destination, artist)):
                        mkdir(join(temp_destination, artist))

                    temp_destination = join(temp_destination, artist)

                    if music_file["album"] is not None:
                        album = make_file_folder_safe_string(music_file["album"])
                        if not isdir(join(temp_destination, album)):
                            mkdir(join(temp_destination, album))

                        temp_destination = join(temp_destination, album)

                replace(file, join(temp_destination, file_name))
            except Exception as exception:
                print("Broken on above file:" + file + " " + str(exception))
    else:
        messagebox.showerror("Org Error", "Source or Destination are not valid directories.")


# Remove all empty folders within a directory
def clean_directory(source: str):
    for temp_dir in listdir(source):
        joined_directory = join(source, temp_dir)
        if isdir(joined_directory) and len(listdir(joined_directory)) == 0:
            os.rmdir(joined_directory)
        elif isdir(joined_directory):
            clean_directory(joined_directory)


# Class for the music file manager
class MusicFileManager(tk.Tk):
    song_index = 0
    song_list = []
    main_mp3_tags = ["title", "artist", "tracknumber", "album", "genre"]
    artist_mp3_tags = ["artist", "artistsort", "albumartist", "albumartistsort"]
    album_mp3_tags = ["album", "albumsort"]
    entry_dictionary = {}
    song = None

    def __init__(self):
        super().__init__()
        super().title("Music Tool")
        super().geometry("1150x825")

        # local variables; only able to be created after initializing Tk()
        self.source = tk.StringVar()
        self.destination = tk.StringVar()
        self.file = tk.StringVar()

        # create a canvas to allow the application to be scrollable
        canvas = tk.Canvas(self, highlightthickness=0)
        scrollbar_vertical = ttk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar_horizontal = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=canvas.xview)

        canvas.configure(yscrollcommand=scrollbar_vertical.set)
        canvas.configure(xscrollcommand=scrollbar_horizontal.set)

        scrollbar_horizontal.pack(side=tk.BOTTOM, fill=tk.X)
        scrollbar_vertical.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        canvas.columnconfigure((0, 1), weight=1)
        canvas.rowconfigure((0, 1), weight=1)

        self.bind(
            '<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox(tk.ALL))
        )

        scrollable_frame = tk.Frame(canvas)

        canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)

        # Frames
        location_frame = tk.Frame(scrollable_frame)
        location_frame.grid(row=0, column=0, sticky=tk.W, pady=5)

        function_frame = tk.Frame(scrollable_frame)
        function_frame.grid(row=0, column=1, rowspan=4, sticky=tk.N, padx=5)

        song_data_frame = tk.Frame(scrollable_frame)
        song_data_frame.grid(row=1, column=0, sticky=tk.W, pady=5)

        song_data_expanded_frame = tk.Frame(scrollable_frame)
        song_data_expanded_frame.grid(row=2, column=0, sticky=tk.W, pady=5)

        # Location Frame
        location_label = tk.Label(location_frame, text="Folder Locations")
        location_label.grid(row=0, column=0, sticky=tk.W)

        source_label = tk.Label(location_frame, text="Source")
        source_label.grid(row=1, column=0, sticky=tk.W)

        source_entry = tk.Entry(location_frame, textvariable=self.source, width=50)
        source_entry.grid(row=1, column=1, sticky=tk.W)

        destination_label = tk.Label(location_frame, text="Destination")
        destination_label.grid(row=2, column=0, sticky=tk.W)

        destination_entry = tk.Entry(location_frame, textvariable=self.destination, width=50)
        destination_entry.grid(row=2, column=1, sticky=tk.W)

        # Function Frame
        function_label = tk.Label(function_frame, text="Functions")
        function_label.grid(row=0, column=0, columnspan=4, sticky=tk.NSEW)

        get_all_songs_button = tk.Button(function_frame, text="Get All Songs", width=8, command=lambda: self.set_song_list())
        get_all_songs_button.grid(row=1, column=0, columnspan=2, sticky=tk.NS)

        get_dir_songs_button = tk.Button(function_frame, text="Get Dir Songs", width=8, command=lambda: self.set_song_list(False))
        get_dir_songs_button.grid(row=1, column=2, columnspan=2, sticky=tk.NS)

        mp3s_button = tk.Button(function_frame, text="Get MP3s", width=8, command=lambda: self.move_files(self.get_mp3s()))
        mp3s_button.grid(row=2, column=0, columnspan=2, sticky=tk.NS)

        mp4s_button = tk.Button(function_frame, text="Get MP4s", width=8, command=lambda: self.move_files(self.get_mp4s()))
        mp4s_button.grid(row=2, column=2, columnspan=2, sticky=tk.NS)

        move_button = tk.Button(function_frame, text="Move", width=8, command=lambda: self.move_files(self.get_song_list()))
        move_button.grid(row=3, column=0, columnspan=2, sticky=tk.NS)

        organize_button = tk.Button(function_frame, text="Organize", width=8,
                                    command=lambda: organize_files(self.source.get(),
                                                                   self.destination.get()))
        organize_button.grid(row=3, column=2, columnspan=2, sticky=tk.NS)

        clean_dir_button = tk.Button(function_frame, text="Clean Dirs", width=8,
                                     command=lambda: clean_directory(self.source.get()))
        clean_dir_button.grid(row=4, column=0, columnspan=4, sticky=tk.NS)

        folder_actions_label = tk.Label(function_frame, text="Folder Actions")
        folder_actions_label.grid(row=5, column=0, columnspan=4, sticky=tk.NSEW)

        update_artist_button = tk.Button(function_frame, text="Update Artist", width=8,
                                         command=lambda: self.update_folder_artist())
        update_artist_button.grid(row=6, column=0, columnspan=2, sticky=tk.NS)

        self.new_artist_input = tk.Entry(function_frame, textvariable=tk.StringVar())
        self.new_artist_input.grid(row=6, column=2, columnspan=2, sticky=tk.NSEW)

        update_album_button = tk.Button(function_frame, text="Update Album", width=8, command=lambda: self.update_folder_album())
        update_album_button.grid(row=7, column=0, columnspan=2, sticky=tk.NS)

        self.new_album_input = tk.Entry(function_frame, textvariable=tk.StringVar())
        self.new_album_input.grid(row=7, column=2, columnspan=2, sticky=tk.NSEW)

        update_genre_button = tk.Button(function_frame, text="Update Genre", width=8, command=lambda: self.update_folder_genre())
        update_genre_button.grid(row=8, column=0, columnspan=2, sticky=tk.NS)

        self.new_genre_input = tk.Entry(function_frame, textvariable=tk.StringVar())
        self.new_genre_input.grid(row=8, column=2, columnspan=2, sticky=tk.NSEW)

        # Song Data Frame
        song_label = tk.Label(song_data_frame, text="Song Information")
        song_label.grid(row=0, column=0, columnspan=6, sticky=tk.NSEW)

        file_label = tk.Label(song_data_frame, text="File")
        file_label.grid(row=1, column=0, sticky=tk.W)

        file_entry = tk.Entry(song_data_frame, textvariable=self.file)
        file_entry.grid(row=1, column=1, sticky=tk.W)

        # All ID3 tags according to EasyID3
        # album, bpm, compilation, composer, copyright, encodedby, lyricist, length, media, mood,
        #   grouping, title, version, artist, albumartist, conductor, arranger, discnumber, organization,
        #   tracknumber, author, albumartistsort, albumsort, composersort, artistsort, titlesort, isrc,
        #   discsubtitle, language, genre, date, originaldate, performer: *, website, replaygain_ * _gain,
        #   replaygain_ * _peak, musicip_puid, musicip_fingerprint, releasecountry, asin, performer,
        #   barcode, catalognumber, acoustid_fingerprint, acoustid_id

        title_label = tk.Label(song_data_frame, text="Title")
        title_label.grid(row=1, column=2, sticky=tk.W)

        title_input = tk.Entry(song_data_frame, textvariable=tk.StringVar())
        title_input.grid(row=1, column=3, sticky=tk.W)
        self.entry_dictionary["title"] = title_input

        artist_label = tk.Label(song_data_frame, text="Artist")
        artist_label.grid(row=1, column=4, sticky=tk.NSEW)

        artist_input = tk.Entry(song_data_frame, textvariable=tk.StringVar())
        artist_input.grid(row=1, column=5, sticky=tk.NSEW)
        self.entry_dictionary["artist"] = artist_input

        track_label = tk.Label(song_data_frame, text="Track Number")
        track_label.grid(row=2, column=0, sticky=tk.NSEW)

        track_input = tk.Entry(song_data_frame, textvariable=tk.StringVar())
        track_input.grid(row=2, column=1, sticky=tk.NSEW)
        self.entry_dictionary["tracknumber"] = track_input

        album_label = tk.Label(song_data_frame, text="Album")
        album_label.grid(row=2, column=2, sticky=tk.NSEW)

        album_input = tk.Entry(song_data_frame, textvariable=tk.StringVar())
        album_input.grid(row=2, column=3,  sticky=tk.NSEW)
        self.entry_dictionary["album"] = album_input

        genre_label = tk.Label(song_data_frame, text="Genre")
        genre_label.grid(row=2, column=4, sticky=tk.NSEW)

        genre_input = tk.Entry(song_data_frame, textvariable=tk.StringVar())
        genre_input.grid(row=2, column=5,  sticky=tk.NSEW)
        self.entry_dictionary["genre"] = genre_input

        back_button = tk.Button(song_data_frame, text="Back", width=5,
                                command=lambda: self.get_previous_song())
        back_button.grid(row=3, column=0, columnspan=2)

        save_button = tk.Button(song_data_frame, text="Save", width=5,
                                command=lambda: self.save_song())
        save_button.grid(row=3, column=2, columnspan=2)

        next_button = tk.Button(song_data_frame, text="Next", width=5,
                                command=lambda: self.get_next_song())
        next_button.grid(row=3, column=4, columnspan=2)

        # Song Data Extended Frame
        expanded_label = tk.Label(song_data_expanded_frame, text="Extended Data")
        expanded_label.grid(row=0, column=0, columnspan=4, sticky=tk.NSEW)

        curr_row = 1
        curr_col = 0
        for index, key in enumerate(filter(lambda x: "musicbrainz" not in x and x not in self.main_mp3_tags,
                                           EasyID3.valid_keys.keys())):
            key_label = tk.Label(song_data_expanded_frame, text=key)
            key_label.grid(row=curr_row, column=curr_col, sticky=tk.NSEW)

            key_input = tk.Entry(song_data_expanded_frame, textvariable=tk.StringVar())
            key_input.grid(row=curr_row, column=curr_col+1, sticky=tk.NSEW)
            self.entry_dictionary[key] = key_input

            if index % 2 == 1:
                curr_row += 1

            if curr_col == 0:
                curr_col = 2
            else:
                curr_col = 0

    def get_previous_song(self):
        if self.song_index > 0:
            self.song_index -= 1
        else:
            self.song_index = len(self.song_list) - 1
        self.set_song_fields(self.song_index)

    def get_next_song(self):
        if self.song_index < len(self.song_list) - 1:
            self.song_index += 1
        else:
            self.song_index = 0
        self.set_song_fields(self.song_index)

    def get_mp4s(self):
        return get_mp4_list([], self.source.get())

    def get_mp3s(self):
        return get_mp3_list([], self.source.get())

    def get_song_list(self):
        return get_list([], self.source.get())

    def set_song_list(self, sub_dir: bool = True):
        self.song_index = 0
        self.song_list = get_list([], self.source.get(), sub_dir=sub_dir)
        self.set_song_fields(self.song_index)

    def move_files(self, files: list):
        move_files(self.destination.get(), self.source.get(), files)
        messagebox.showinfo("Move Info", "Move complete.")

    def set_song_fields(self, index: int):
        try:
            self.song = MP3(self.song_list[index], ID3=EasyID3)
            self.file.set(os.path.basename(self.song.filename))

            for key in filter(lambda x: "musicbrainz" not in x, EasyID3.valid_keys.keys()):
                self.entry_dictionary.get(key).delete(0, tk.END)

                if self.song.get(key) is not None:
                    self.entry_dictionary.get(key).insert(0, str(self.song.get(key)[0]))

        except MutagenError:
            print(f"File {self.song_list[index]} was not a valid audio file.")
            self.get_next_song()

    def save_song(self):
        print("Saving...")
        # save all tags that have been updated
        for key in filter(lambda x: "musicbrainz" not in x, EasyID3.valid_keys.keys()):
            # create and update
            if self.entry_dictionary.get(key).get() != "":
                # verify what is added is valid to the field; with check if empty (removed)
                self.song[key] = self.entry_dictionary.get(key).get()
            # remove key if set field to blank
            elif key in self.song.keys() and self.entry_dictionary.get(key).get() == "":
                self.song.pop(key=key)

        # save the song
        self.song.save()

        # change the name if updated
        if self.file.get() != os.path.basename(self.song.filename):
            print("Renaming file")

            rename(self.song.filename, join(Path(self.song.filename).parent, self.file.get()))
            self.song.filename = join(Path(self.song.filename).parent, self.file.get())

            # update it within the list if the name is different
            self.song_list[self.song_index] = join(Path(self.song.filename).parent, self.file.get())
            print("New file at: " + self.song_list[self.song_index])

        messagebox.showinfo("Info", "Song saved!")

    def update_folder_artist(self):
        print("Updating folder artist")
        new_artist = self.new_artist_input.get().strip()
        self.mass_update(self.artist_mp3_tags, new_artist)

    def update_folder_album(self):
        print("Updating folder album")
        new_album = self.new_album_input.get().strip()
        self.mass_update(self.album_mp3_tags, new_album)

    def update_folder_genre(self):
        print("Updating folder genre")
        new_genre = self.new_genre_input.get().strip()
        self.mass_update(["genre"], new_genre)

    def mass_update(self, keys: list, data: str):
        songs = get_mp3_list([], self.source.get())
        new_data = data.strip()
        if new_data != "":
            for song in songs:
                mp3_song = MP3(song, ID3=EasyID3)
                for key in keys:
                    if "sort" in key and new_data.startswith("The "):
                        # remove "The " for sorting data
                        mp3_song[key] = new_data[4:]
                    else:
                        mp3_song[key] = new_data
                mp3_song.save()

        messagebox.showinfo("Info", "Mass update complete!")


if __name__ == '__main__':
    app = MusicFileManager()
    app.mainloop()
