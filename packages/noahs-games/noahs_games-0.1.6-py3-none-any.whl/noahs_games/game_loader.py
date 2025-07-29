from noahs_google_drive_downloader import download_google_drive_folder, download_google_drive_file
import subprocess
import os
import sys


def load_game(game="zombie_shooter"):
	if game == "zombie_shooter":
		# download_google_drive_folder(
		# 	folder_url="https://drive.google.com/drive/folders/1DzFshn1iYdwpn6bO_pmZa1BMFuchuDjn?usp=drive_link",
		# 	output_dir="zombie_shooter"
		# )
		download_google_drive_file(
			url="https://drive.google.com/file/d/1I8INrFGhD6_2GJlRVA2GpKE17uxZknpX/view?usp=sharing",
			output_path="zombie_shooter.zip"
		)
	else:
		print("game " + game + " not found")


# def play_game(game="zombie_shooter"):
# 	load_game(game)
# 	subprocess.run(
# 		["python", "main.py"],
# 		cwd=os.path.join(os.getcwd(), "zombie_shooter")
# 	)


def play_game(game="zombie_shooter"):
	load_game(game)
	subprocess.run(
		[sys.executable, "main.py"],
		cwd=os.path.join(os.getcwd(), "zombie_shooter")
	)