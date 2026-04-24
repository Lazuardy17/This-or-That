from flask import Flask, render_template, request, session, redirect, url_for
import random

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        raw_items = request.form.get('items', '')
        items = [item.strip() for item in raw_items.split('\n') if item.strip()]

        if len(items) < 2:
            return render_template('index.html', error="Need at least 2 items bro.", raw_items=raw_items)

        if len(items) > 100:
            return render_template('index.html', error=f"I said max 100 items. You entered {len(items)} items. Please comply.", raw_items=raw_items)
        
        random.shuffle(items) 
        
        session['items'] = items
        session['sorted'] = [items[0]] 
        session['curr_idx'] = 1        
        session['cmp_idx'] = 0         
        
        return redirect(url_for('vote'))

    return render_template('index.html', raw_items='')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'items' not in session:
        return redirect(url_for('index'))

    if session['curr_idx'] >= len(session['items']):
        return redirect(url_for('result'))

    curr_item = session['items'][session['curr_idx']]
    cmp_item = session['sorted'][session['cmp_idx']]

    if request.method == 'POST':
        winner = request.form.get('winner')
        
        if winner == 'curr':
            session['sorted'].insert(session['cmp_idx'] + 1, curr_item)
            session['curr_idx'] += 1
            session['cmp_idx'] = len(session['sorted']) - 1
        else:
            session['cmp_idx'] -= 1
            if session['cmp_idx'] < 0:
                session['sorted'].insert(0, curr_item)
                session['curr_idx'] += 1
                session['cmp_idx'] = len(session['sorted']) - 1
                
        session.modified = True
        return redirect(url_for('vote'))

    progress = int((session['curr_idx'] / len(session['items'])) * 100)
    return render_template('vote.html', curr=curr_item, cmp=cmp_item, progress=progress)

@app.route('/result')
def result():
    if 'sorted' not in session:
        return redirect(url_for('index'))
    final_ranking = list(reversed(session['sorted']))
    session.clear()
    return render_template('result.html', items=final_ranking)

if __name__ == '__main__':
    app.run(debug=True)
