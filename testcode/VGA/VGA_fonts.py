# Font library reused from the xglcd font library by rdagger
# https://github.com/rdagger/micropython-ili9341/tree/master

class Font:
    """Font data in X-GLCD format.

    Attributes:
        letters: A bytearray of letters (columns consist of bytes)
        font_width: Maximum pixel width of font
        font_height: Pixel height of font
        start_letter: ASCII number of first letter
        bytes_per_letter: How many bytes in one letter

    Note:
        Font files can be generated with the free version of MikroElektronika
        GLCD Font Creator:  www.mikroe.com/glcd-font-creator
        The font file must be in X-GLCD 'C' format.
        To save text files from this font creator program in Win7 or higher
        you must use XP compatibility mode or you can just use the clipboard.
    """

    def __init__(self, path, width, height, start_letter=32, letter_count=96, char_spacing=1, line_spacing=2):
        """Constructor for X-GLCD Font object.

        Args:
            path (string): Full path of font file
            width (int): Maximum width in pixels of each letter
            height (int): Height in pixels of each letter
            start_letter (int): First ASCII letter.  Default is 32.
            letter_count (int): Total number of letters.  Default is 96.
            char_spacing (int) pixels between char when pronting multiple chars
            line_spacing (int) pixels between lines when line feed
        """
        self.width = width
        self.height = max(height, 8)
        self.start_letter = start_letter
        self.letter_count = letter_count
        self.bytes_per_letter = (int(
            (self.height - 1) / 8) + 1) * self.width + 1
        self.load_xglcd_font(path)
        self.char_spacing = char_spacing
        self.line_spacing = line_spacing

    def load_xglcd_font(self,font_filename):
        print(font_filename)
        self.letters = bytearray(self.bytes_per_letter * self.letter_count)
        offset=0
        with open(font_filename, 'r') as f:
                for line in f:
                    # Skip lines that do not start with hex values
                    line = line.strip()
                    if len(line) == 0 or line[0:2] != '0x':
                        continue
                    # Remove comments
                    comment = line.find('//')
                    if comment != -1:
                        line = line[0:comment].strip()
                    # Remove trailing commas
                    if line.endswith(','):
                        line = line[0:len(line) - 1]
                    # Convert hex strings to bytearray and insert in to letters
                    self.letters[offset: offset + self.bytes_per_letter] = bytearray(
                        int(b, 16) for b in line.split(','))
                    offset += self.bytes_per_letter
    
    def Get_letter(self,char):
        init_index=(ord(char)-self.start_letter)*self.bytes_per_letter
        letter=self.letters[init_index:init_index+self.bytes_per_letter]
        return(letter)
