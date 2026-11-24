# ----------------------------------------------------------------------------

def swtor_stb_to_dict(filepath, skip_empty=True):
    """
    Convert a SWTOR .stb string-table file into a dict of {full_id: text}.

    Keys   : full 64-bit string ID (int)
    Values : decoded, stripped UTF-8 text (str)

    Note: some entries have zero-length text by design (e.g. unused
    gender-variant lines in conversation files). Set skip_empty=True
    to exclude these from the returned dict.
    
    WHAT THIS DOES
        Reads a binary .stb file (SWTOR's compiled localization string
        table format, found under /resources/<locale>/str/...) and
        returns a plain Python dict mapping each entry's unique 64-bit
        string ID to its text content.

    FILE FORMAT (little-endian)
        Header (7 bytes):
            bytes 0-2  magic marker, must equal 01 00 00
            bytes 3-6  uint32, number of string entries in the file

        Entry table (26 bytes per entry, starts right after the header):
            +0   uint64  full_id      - unique string ID (dict key)
            +8   uint16  bitflag      - unused for text extraction
            +10  uint32  version      - unused for text extraction
            +14  uint32  text_length  - byte length of the string
            +18  uint32  text_offset  - absolute file offset of the string

        String data:
            UTF-8 bytes located at text_offset, text_length bytes long.

    ZERO-LENGTH ENTRIES
        Some IDs legitimately have a text_length of 0 in the file itself
        (e.g. unused gender-variant lines in conversation files). These
        are not parsing errors. By default they're kept as empty strings;
        pass skip_empty=True to leave them out of the returned dict.

    Args:
        filepath (str): path to the .stb file on disk.
        skip_empty (bool): if True, omit entries with zero-length text.

    Returns:
        dict[int, str]: full_id -> text.

    Raises:
        ValueError: if the file doesn't start with the expected .stb magic.
    """


    import struct


    with open(filepath, "rb") as f:
        data = f.read()

    magic = struct.unpack_from("<I", data, 0)[0]
    if (magic & 0xFFFFFF) != 1:
        raise ValueError(f"Not a valid .stb file: {filepath}")

    entry_count = struct.unpack_from("<I", data, 3)[0]

    ENTRY_SIZE = 26
    TABLE_START = 7

    result = {}
    for i in range(entry_count):
        base = TABLE_START + i * ENTRY_SIZE

        full_id = struct.unpack_from("<Q", data, base)[0]
        text_length = struct.unpack_from("<I", data, base + 14)[0]
        text_offset = struct.unpack_from("<I", data, base + 18)[0]

        if text_length == 0:
            if skip_empty:
                continue
            result[full_id] = ""
            continue

        raw_text = data[text_offset:text_offset + text_length]
        result[full_id] = raw_text.decode("utf-8").strip()

    return result

# -----------

def swtor_stb_to_dict_debug(filepath, limit=20):
    """
    Print raw field values per entry so you can see whether empty strings
    come from a real zero-length field in the file, or from text_offset
    pointing at the wrong place (misalignment).
    """
    
    
            
    import struct



    with open(filepath, "rb") as f:
        data = f.read()

    entry_count = struct.unpack_from("<I", data, 3)[0]
    ENTRY_SIZE = 26
    TABLE_START = 7

    for i in range(min(entry_count, limit)):
        base = TABLE_START + i * ENTRY_SIZE
        full_id = struct.unpack_from("<Q", data, base)[0]
        text_length = struct.unpack_from("<I", data, base + 14)[0]
        text_offset = struct.unpack_from("<I", data, base + 18)[0]

        # Where does the string table actually start? Entries end here:
        table_end = TABLE_START + entry_count * ENTRY_SIZE

        print(
            f"entry {i}: id={full_id} len={text_length} offset={text_offset} "
            f"offset_in_range={text_offset >= table_end}"
        )

# ----------------------------------------------------------------------------

