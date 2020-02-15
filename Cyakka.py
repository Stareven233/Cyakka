from app import create_app, create_db_table
from app.fake import create_fake_data

app = create_app()


if __name__ == '__main__':
    # create_db_table(app)
    # create_fake_data(app)
    app.run(debug=True)
