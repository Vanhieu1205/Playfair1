from flask import Flask, request, render_template
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'


# Function to convert the string to lowercase
def toLowerCase(plain):
    return plain.lower()


# Function to remove all spaces in a string
def removeSpaces(plain):
    return plain.replace(" ", "")


# Function to generate the 5x5 key square
def generateKeyTable(key):
    key = key.lower().replace(' ', '').replace('j', 'i')
    key_square = ''
    for letter in key + 'abcdefghiklmnopqrstuvwxyz':
        if letter not in key_square:
            key_square += letter
    return key_square


# Function to search for the characters of a digraph
# in the key square and return their position (for encryption)
def search_encrypt(key_square, a, b):
    if a == 'j':
        a = 'i'
    elif b == 'j':
        b = 'i'
    row_a, col_a = divmod(key_square.index(a), 5)
    row_b, col_b = divmod(key_square.index(b), 5)
    if row_a == row_b:
        col_a = (col_a + 1) % 5
        col_b = (col_b + 1) % 5
    elif col_a == col_b:
        row_a = (row_a + 1) % 5
        row_b = (row_b + 1) % 5
    else:
        col_a, col_b = col_b, col_a
    return key_square[row_a * 5 + col_a] + key_square[row_b * 5 + col_b]


# Function to search for the characters of a digraph
# in the key square and return their position (for decryption)
def search_decrypt(key_square, a, b):
    if a == 'j':
        a = 'i'
    elif b == 'j':
        b = 'i'
    row_a, col_a = divmod(key_square.index(a), 5)
    row_b, col_b = divmod(key_square.index(b), 5)
    if row_a == row_b:
        col_a = (col_a - 1) % 5  # Reverse the column movement
        col_b = (col_b - 1) % 5
    elif col_a == col_b:
        row_a = (row_a - 1) % 5  # Reverse the row movement
        row_b = (row_b - 1) % 5
    else:
        col_a, col_b = col_b, col_a
    return key_square[row_a * 5 + col_a] + key_square[row_b * 5 + col_b]


# Function for performing the encryption
def encrypt(plain, key_square):
    plain = removeSpaces(toLowerCase(plain))
    encrypted = ''
    i = 0
    while i < len(plain):
        if i == len(plain) - 1 or plain[i] == plain[i + 1]:
            encrypted += plain[i] + 'x'
        else:
            encrypted += plain[i] + plain[i + 1]
            i += 1
        i += 1
    result = ''
    for i in range(0, len(encrypted), 2):
        result += search_encrypt(key_square, encrypted[i], encrypted[i + 1])
    return result.upper()


# Function for performing the decryption
def decrypt(ciphertext, key_square):
    # Loại bỏ các khoảng trắng khỏi văn bản mã hóa
    ciphertext = ciphertext.replace(" ", "")

    decrypted = ''
    i = 0
    while i < len(ciphertext):
        a = ciphertext[i].lower()
        if i + 1 < len(ciphertext):
            b = ciphertext[i + 1].lower()
        else:
            # If there's only one character left in the ciphertext, add 'x' to form a digraph
            b = 'x'

        if a == b:  # Trường hợp có cặp ký tự trùng nhau
            b = 'x'
            i -= 1  # Lùi lại 1 vị trí để xử lý cặp ký tự tiếp theo
        decrypted += search_decrypt(key_square, a, b)
        i += 2

    # Kiểm tra xem chuỗi đã giải mã có độ dài lẻ không, nếu có thì thêm 'x' vào cuối
    if len(decrypted) % 2 != 0:
        decrypted += 'x'

    return decrypted.upper()


# Form to input plaintext and key
class EncryptForm(FlaskForm):
    key = TextAreaField('Enter Key:', validators=[DataRequired()])
    plaintext = TextAreaField('Message to Encrypt/Decrypt:', validators=[DataRequired()])
    submit = SubmitField('Submit')


# Route for the main page
@app.route('/', methods=['GET', 'POST'])
def index():
    form = EncryptForm()
    if form.validate_on_submit():
        plaintext = form.plaintext.data
        key = form.key.data
        key_square = generateKeyTable(key)

        # Check if the form is submitted for encryption or decryption
        if 'encrypt' in request.form:
            result_text = encrypt(plaintext, key_square)
            return render_template('index.html', form=form, result_text=result_text)
        elif 'decrypt' in request.form:
            result_text = decrypt(plaintext, key_square)
            return render_template('index.html', form=form, result_text=result_text)
    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
