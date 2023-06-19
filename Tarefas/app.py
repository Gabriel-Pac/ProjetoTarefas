import sqlite3
import os
from flask import Flask, render_template, request, url_for, flash, redirect
from datetime import datetime 
from date_time_checker import check_datetime
from datetime import datetime,date

# cria a conexao com o BD
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# query todos os posts no banco
def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    return post

# cria o serviço
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SESSION_SECRET_KEY_DEV')


# definicao das rotas
@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()

    tempo_real = datetime.now().time()
    data_atual= date.today()

    return render_template('index.html', posts=posts, tempo_real=tempo_real,  data_atual= data_atual)

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        return render_template('404.html')
    return render_template('post.html', post=post)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        deadline = request.form['deadline']
        deadlineDate = request.form['deadlineDate']
        
        if not title or not content or not deadline or not deadlineDate:
            flash('Título, conteúdo, prazo final e data limite são obrigatórios!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content, deadline, deadlineDate) VALUES (?, ?, ?, ?)',
                         (title, content, deadline, deadlineDate))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if post is None:
        return render_template('404.html')

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        deadline = request.form['deadline']
        deadlineDate = request.form['deadlineDate']
  
        if not title or not content or not deadline or not deadlineDate:
            flash('Título, conteúdo, prazo final e data limite são obrigatórios!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?, deadline = ?, deadlineDate = ? WHERE id = ?',
                 (title, content, deadline, deadlineDate, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    if post is None:
        return render_template('404.html')
    
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" A tarefa foi excluída com sucesso!'.format(post['title']))
    return redirect(url_for('index'))

@app.route('/rota')
def data_atual():
    selected_date = datetime.now().date()
    return render_template('seu_template.html', selected_date=selected_date, posts="posts")

@app.template_filter('inf_data')
def data(inf_data):
    return datetime.strptime(inf_data, '%Y-%m-%d').date()

@app.template_filter('inf_tempo')
def string_to_time(inf_tempo):
    return datetime.strptime(inf_tempo, '%H:%M').time()

# inicia servico
if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=5000)
