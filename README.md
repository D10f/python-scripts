# python-scripts

A collection of small scripts written in Python and implemented as command line utility programs.

#### [Batch Resizer](https://github.com/herokunt/python-scripts/blob/main/batch-resizer.py)
Process images by converting them to different formats, resizing them and store them as compressed archives for easy upload to your cloud. You may provide one or more images and they'll be processed in parallel for extra speed. File metadata like GPS location, camera model, etc., is completely removed.

```
# Resize images to a specified width and height (aspect ratio preserved)
$ resizer.py ~/Pictures/* --resize 600 600

# Convert images to the specified format or formats (JPEG, PNG or WEBP)
$ resizer.py ~/Pictures/* --format jpeg webp

# Provide target directory for output images
$ resizer.py ~/Pictures/* --output ~/Desktop

# Create an archive for the output processed images with a custom name
$ resizer.py ~/Pictures/* -o ~/Desktop -t backup
```

---
#### [Password Checker](https://github.com/herokunt/python-scripts/blob/main/password_checker.py)
Check your passwords against the popular "Have I Been Pwned?" website and find out if they've been leaked in any of the increasingly common data breaches. Your passwords provided to the script will remain secured as only a hash is used, as per the Have I Been Pwned API requires.

You can provide passwords inline or through a CSV file, ideal if your password manager (such as KeePassXC) supports exporting data in CSV format. For security you can instruct the script to securely delete that file from your hard drive by overwriting the original contents with random bytes before deleting it.

```
$ ./password_checker.py password1 123456 -f ~/Desktop/path_to_file.csv --delete --verbose
Found match for "Gmail" 1444 times!
Found match for "pas..." 2427158 times!
Found match for "123..." 24230577 times!
DEBUG:root:Securely deleting file (3 rounds...)
```

---
#### [File Organizer](https://github.com/herokunt/python-scripts/blob/main/file_organizer.py)
Automate the boring task of organizing your files into a neat folder structure. This script will look at your files inside the Downloads folder and move them to where they belong based on the file extension. If you have hundreds of files in there this will clear things up in the blink of an eye!.

Provide additional options to customize which files you want to move around and where to send them. Run it in test-mode to see first what changes would be make to avoid any mistakes. For best results, run this automatically using a scheduler like `cron` and combine it with the following script in the list.

Examples:

```bash
# Move only files with extension .mp4 and .wav
./file_organizer.py -o mp4 wav

# Move all files except those with extension .mp4 and .wav
./file_organizer.py -i mp4 wav

# Move all .epub and .mobi files to ~/Shared/Books (default for .epub and .mobi is ~/Documents)
./file_organizer.py -m ~/Shared/Books=epub,pdf

# Move files from ~/Desktop (default is to move from ~/Downloads)
./file_organizer.py -s ~/Desktop

# Move files with multiple extensions to the Desktop e.g.: Shade of Z - Black.tar.xz, files_backup.tar.gz
./file_organizer.py -e '(\.tar\.[gx]z)$' -m ~/Desktop=.tar.gz,.tar.xz

# Run in test mode to verify changes before actually writing to disk
./file_organizer.py --dry-run
```

Todo:
- [ ] Allow using -f to force overwrite existing files, or create copies
- [ ] Create missing directories when specified as destination source 
for moved files.
- [X] Improve dry-run output for clarity
- [X] Improve logging verbosity, add colors and clear format.
- [ ] Support for multiple sources e.g, Desktop and Downloads


---
#### [Nama Nama](https://github.com/herokunt/python-scripts/blob/main/nama_nama.py)
"Nama" means name in some languages such as Malay or Indonesian. This small utility script will help organize any collection of files by renaming them uniformly, adding prefixes and sufixes, custom separators, etc. Ideal for music, images, books and other types of documents that have uneven format (mixed of uppercase and lowercase, underscores with spaces, etc). Before, and after:

```
$ ls ~/Documents/books/linux
'Ansible for DevOps.epub'
 grep.pdf
'Introduction to Linux.pdf'
'Learn Linux in 5 days.pdf'
'Linux BASH Programming Cookbook.pdf'
 linuxsys.pdf
 sed.pdf

$ nama_nama.py ~/Documents/books/linux --title --split --separate _ --dry-run
Ansible_For_Devops.epub
Sed.pdf
Grep.pdf
Introduction_To_Linux.pdf
Linux_Bash_Programming_Cookbook.pdf
Linuxsys.pdf
Learn_Linux_In_5_Days.pdf
```

---
#### [Oh, Node!](https://github.com/herokunt/python-scripts/blob/main/oh_node.py)
Curious about how many files does that node_modules folder has in it? How many lines of code? What kind of files are in there? This small utility script will find out for you exactly that!

```
$ oh_node.py ~/Projects/ -t 10
oh_node.py - Scan Complete
--------------------------------------------------
Total files.................................129514
  Showing 10 most common extensions
  js.........................................80095
  json.......................................10800
  ts..........................................8897
  map.........................................3668
  md..........................................2486
  yml.........................................1202
  flow........................................1191
  png..........................................494
  npmignore....................................452
  txt..........................................362
Total size.................................657.9MB
Total lines of code.......................14504117
```

---
#### [Scanner](https://github.com/herokunt/python-scripts/blob/main/scanner.py)
A simple but functional port scanner to find out which ports are open in your local network. Specify the host by IP or name, and optionally the range of ports to scan in the host.

---
#### [Zombie Dice](https://github.com/herokunt/python-scripts/blob/main/zombiedice.py)
Zombie Dice is a "press your luck" party dice game created by Steve Jackson Games. Following along the "Automating the Boring Stuff With Python" book by Al Sweigart I wrote this script that plays this game using bots.

---
#### [Conway's Game of Life](https://github.com/herokunt/python-scripts/blob/main/conway.py)
The classic Game of Life has three simple rules, but can be complex enough to build entire computational systems with it; I highly recommend to watch the first few minutes of this [great talk about The Art of Code](https://www.youtube.com/watch?v=gdSlcxxYAA8). Following along the "Automating the Boring Stuff With Python" book by Al Sweigart this is an attempt to write the game in a (hopefully) cleaner and more pythonic way.


---
#### [Collatz Sequence](https://github.com/herokunt/python-scripts/blob/main/collatz.py)
Following along the "Automating the Boring Stuff With Python" book by Al Sweigart this is a script that runs from the terminal, taking one number and following the "Collatz Conjecture" rules where any positive number will eventually and invariable be reduced down to 1.  

---
#### [Caesar's cipher](https://github.com/herokunt/python-scripts/blob/main/ciphers/caesar-chiper.py)
One of the most popular ciphers used over 2000 years ago. Following along the "Cracking Codes With Python" book by Al Sweigart, this is an attempt to create an improved and flexible implementation of the cipher that works from the command line. It supports the expected operations of encryption, decryption as well as key derivation and brute forcing.

```
$ caesar-cipher.py -e 'common sense is not that common' 17
t^$$^% )v%)v z) %^_ _yr_ t^$$^%
```

```
$ caesar-cipher.py -k 'common sense is not that common' 't^$$^% )v%)v z) %^_ _yr_ t^$$^%'
The key used to encrypt this message was 17
```
---

#### [Transposition cipher](https://github.com/herokunt/python-scripts/blob/main/ciphers/transposition-cipher.py)
A cipher that works by laying the letters of a message in a grid of varying size and encrypting the message from it. Following along the "Cracking Codes With Python" book by Al Sweigart, this is an attempt to create an improved and flexible implementation of the cipher that works from the command line. It supports the expected operations of encryption, decryption as well as key derivation and brute forcing.

```
$ transposition-cipher.py -e 'Batch resizer is a small utility script that looks at a directory and processes all images in it in some way. You can resize them, convert them into other formats or bundle them together in a nice compressed archive, ready to be uploaded.' 99
B oasmtopcmrhee  srwseaesydi. z aeYrroc uhi iscv aean,   srrmeeasalidlzy e u tttoih lebimet, y u cpsolcnorvaiedprettd  .tthhaetm  lionotkos  oatth ear  dfiorremcattosr yo ra nbdu npdrloec etshseems  taolgle tihmearg eisn  ian  niitc ei nc
```

```
$ transposition-cipher.py -d 'B oasmtopcmrhee  srwseaesydi. z aeYrroc uhi iscv aean,   srrmeeasalidlzy e u tttoih lebimet, y u cpsolcnorvaiedprettd  .tthhaetm  lionotkos  oatth ear  dfiorremcattosr yo ra nbdu npdrloec etshseems  taolgle tihmearg eisn  ian  niitc ei nc' 99
Batch resizer is a small utility script that looks at a directory and processes all images in it in some way. You can resize them, convert them into other formats or bundle them together in a nice compressed archive, ready to be uploaded.
```

---
#### [Affine Cipher](https://github.com/herokunt/python-scripts/blob/main/ciphers/affine_cipher.py)
A combination of the Caesar cipher and Multiplicative cipher to create stronger encryption. Following along the "Cracking Codes With Python" book by Al Sweigart, this script is very simple to use from the command line to encrypt, decrypt or brute force any ciphertext encrypted using this cipher.

```
$ affine_cipher.py -e 'Hello GitHub viewers, thank you for checking this one out!'
The encryption key is: 4351
#fYYV $bQ#Pi ObfNfSR, QcjWZ LVP eVS hcfhZbWd QcbR VWf VPQJ
```

---
#### [Simple Substitution Cipher](https://github.com/herokunt/python-scripts/blob/main/ciphers/simple_sub_cipher.py)
A substitution cipher uses a re-arranged alphabet (in this case English alphabet) as the key to encrypt a message. This results in too many possible combinations to brute force through each of them in a reasonable amount of time, but can be hacked through cross-referencing each letter from the message. Because of this, it's also most effective the longer the encrypted message. Following along the "Cracking Codes With Python" book by Al Sweigart, this is an implementation that can be used from the command line.

Encryption:
```
$ simple_sub_cipher.py -e "The Ministry of Truth contained, it was said, three thousand rooms above ground level... Scattered about London there were just three other buildings of similar appearance and size... They were the homes of the four Ministries between which the entire apparatus of government was divided. The Ministry of Truth, which concerned itself with news, entertainment, education, and the fine arts. The Ministry of Peace, which concerned itself with war. The Ministry of Love, which maintained law and order. And the Ministry of Plenty, which was responsible for economic affairs."

The encryption key is: OKXAUPCVQBISTNZHYDJWRMEGLF
Wvu Tqnqjwdl zp Wdrwv xznwoqnua, qw eoj joqa, wvduu wvzrjona dzztj okzmu cdzrna sumus... Jxowwudua okzrw Sznazn wvudu eudu brjw wvduu zwvud krqsaqncj zp jqtqsod ohhuodonxu ona jqfu... Wvul eudu wvu vztuj zp wvu pzrd Tqnqjwdquj kuweuun evqxv wvu unwqdu ohhodowrj zp czmudntunw eoj aqmqaua. Wvu Tqnqjwdl zp Wdrwv, evqxv xznxudnua qwjusp eqwv nuej, unwudwoqntunw, uarxowqzn, ona wvu pqnu odwj. Wvu Tqnqjwdl zp Huoxu, evqxv xznxudnua qwjusp eqwv eod. Wvu Tqnqjwdl zp Szmu, evqxv toqnwoqnua soe ona zdaud. Ona wvu Tqnqjwdl zp Hsunwl, evqxv eoj dujhznjqksu pzd uxznztqx oppoqdj.
```

Cross-reference attack:
```
$ simple_sub_cipher.py -f "Wvu Tqnqjwdl zp Wdrwv xznwoqnua, qw eoj joqa, wvduu wvzrjona dzztj okzmu cdzrna sumus... Jxowwudua okzrw Sznazn wvudu eudu brjw wvduu zwvud krqsaqncj zp jqtqsod ohhuodonxu ona jqfu... Wvul eudu wvu vztuj zp wvu pzrd Tqnqjwdquj kuweuun evqxv wvu unwqdu ohhodowrj zp czmudntunw eoj aqmqaua. Wvu Tqnqjwdl zp Wdrwv, evqxv xznxudnua qwjusp eqwv nuej, unwudwoqntunw, uarxowqzn, ona wvu pqnu odwj. Wvu Tqnqjwdl zp Huoxu, evqxv xznxudnua qwjusp eqwv eod. Wvu Tqnqjwdl zp Szmu, evqxv toqnwoqnua soe ona zdaud. Ona wvu Tqnqjwdl zp Hsunwl, evqxv eoj dujhznjqksu pzd uxznztqx oppoqdj."

Tve Ministrl of Trutv contained, it eas said, tvree tvousand rooms above ground level... Scattered about London tvere eere bust tvree otver buildings of similar appearance and sife... Tvel eere tve vomes of tve four Ministries beteeen evicv tve entire apparatus of government eas divided. Tve Ministrl of Trutv, evicv concerned itself eitv nees, entertainment, education, and tve fine arts. Tve Ministrl of Peace, evicv concerned itself eitv ear. Tve Ministrl of Love, evicv maintained lae and order. And tve Ministrl of Plentl, evicv eas responsible for economic affairs.
```

---
#### [Vigenere Cipher](https://github.com/herokunt/python-scripts/blob/main/ciphers/vigenere_cipher.py)
Following along the "Cracking Codes With Python" book by Al Sweigart, this is an implementation of the Vigenere cipher that can be used from the command line.
