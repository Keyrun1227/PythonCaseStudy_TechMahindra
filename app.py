from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize the database
if not os.path.exists('database.json'):
    with open('database.json', 'w') as f:
        json.dump({}, f)

# Load database
def load_database():
    try:
        with open('database.json', 'r') as f:
            return json.load(f)  # Load and return JSON content
    except json.JSONDecodeError:
        # If the file is empty or corrupted, return an empty dictionary
        return {}


# Save database
def save_database(data):
    with open('database.json', 'w') as f:
        json.dump(data, f, indent=4) 

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Create account
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        try:
            account_number = request.form['account_number']
            name = request.form['name']
            initial_balance = float(request.form.get('initial_balance', 0.0))  # Fallback to 0.0 if not present
            
            # Load database
            db = load_database()
            
            # Check if account already exists
            if account_number in db:
                flash(f"Account {account_number} already exists!", "danger")
            else:
                # Create new account
                db[account_number] = {
                    'name': name,
                    'balance': initial_balance,
                    'transactions': []
                }
                
                # Save updated database
                save_database(db)
                
                flash(f"Account {account_number} created successfully!", "success")
        except KeyError as e:
            flash(f"Error: Missing form field {str(e)}", "danger")
        return redirect(url_for('home'))
    return render_template('create_account.html')


# View account details
@app.route('/view_account', methods=['GET', 'POST'])
def view_account():
    if request.method == 'POST':
        account_number = request.form['account_number']
        db = load_database()
        account = db.get(account_number)

        if account:
            return render_template('view_account.html', account_number=account_number, account=account)
        else:
            flash('Account not found!', 'danger')
            return redirect(url_for('view_account'))
    return render_template('view_account.html')


# Withdraw money
@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if request.method == 'POST':
        account_number = request.form['account_number']
        amount = float(request.form['amount'])
        db = load_database()

        if account_number in db:
            if db[account_number]['balance'] >= amount:
                db[account_number]['balance'] -= amount
                db[account_number]['transactions'].append(f'Withdrawn: {amount}')
                save_database(db)
                flash(f'Successfully withdrawn ₹{amount} from account {account_number}.', 'success')
            else:
                flash('Insufficient balance!', 'danger')
        else:
            flash('Account not found!', 'danger')

        return redirect(url_for('withdraw'))

    return render_template('withdraw.html')


# Deposit money
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        account_number = request.form['account_number']
        amount = float(request.form['amount'])
        db = load_database()

        if account_number in db:
            db[account_number]['balance'] += amount
            db[account_number]['transactions'].append(f'Deposited: {amount}')
            save_database(db)
            flash(f'Successfully deposited ₹{amount} into account {account_number}.', 'success')
        else:
            flash('Account not found!', 'danger')

        return redirect(url_for('deposit'))

    return render_template('deposit.html')



# Fund transfer
@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if request.method == 'POST':
        from_account = request.form['from_account']
        to_account = request.form['to_account']
        amount = float(request.form['amount'])
        db = load_database()

        if from_account in db and to_account in db:
            if db[from_account]['balance'] >= amount:
                db[from_account]['balance'] -= amount
                db[to_account]['balance'] += amount
                db[from_account]['transactions'].append(f'Transferred ₹{amount} to {to_account}')
                db[to_account]['transactions'].append(f'Received ₹{amount} from {from_account}')
                save_database(db)
                flash(f'Transferred ₹{amount} from {from_account} to {to_account}.', 'success')
            else:
                flash('Insufficient balance in the source account!', 'danger')
        else:
            flash('One or both accounts not found!', 'danger')

        return redirect(url_for('transfer'))

    return render_template('transfer.html')

# Print transactions
@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    if request.method == 'POST':
        account_number = request.form['account_number']
        db = load_database()
        account = db.get(account_number)

        if account:
            return render_template('transactions.html', account_number=account_number, transactions=account['transactions'])
        else:
            flash('Account not found!', 'danger')
            return redirect(url_for('home'))
    return render_template('transactions.html')


if __name__ == '__main__':
    app.run(debug=True)
