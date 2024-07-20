def file_read(path):
    f = open(path, 'r', encoding='utf-8')
    content = f.read()
    f.close()

    return content

def file_write(path, content):
    f = open(path, 'w', encoding='utf-8')
    f.write(content)
    f.close()

def file_add(path, content):
    f = open(path, 'a', encoding='utf-8')
    f.write(content)
    f.close()

if __name__ == "__main__":
    PATH = "project4/test.txt"

    content = file_read(PATH)
    print(content)

    new = "overwrited line1\noverwrited line2\n"
    file_write(PATH, new)
    content = file_read(PATH)
    print(content)

    new = "new line1\nnew line2\n"
    file_add(PATH, new)
    content = file_read(PATH)
    print(content)