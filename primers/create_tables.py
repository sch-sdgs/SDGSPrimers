import sqlite3
import argparse
from primers.db_commands import Users


def create_db(conn):
    pp = conn.cursor()
    pp.executescript('drop table if exists users;')

    try:
        pp.executescript("begin")
        pp.executescript("""
        CREATE TABLE users
            (id INTEGER PRIMARY KEY, username varchar(20), admin INTEGER,  UNIQUE(username));
        """)

        pp.executescript("""
            CREATE TABLE boxes
                (id INTEGER PRIMARY KEY, name varchar(20), freezer_id INTEGER, rows INTEGER, columns INTEGER, aliquots INTEGER, user INTEGER, FOREIGN KEY(freezer_id) REFERENCES freezers(id), FOREIGN KEY(user) REFERENCES users(id));
            """)

        pp.executescript("""
            CREATE TABLE freezers
                (id INTEGER PRIMARY KEY, name varchar(20), location varchar(20), user INTEGER, FOREIGN KEY(user) REFERENCES users(id) );
            """)

        pp.executescript("""
            CREATE TABLE applications
                (id INTEGER PRIMARY KEY, name varchar(20), paired INTEGER);
            """)

        pp.executescript("""
                    INSERT into applications
                        (name,paired) VALUES ("Sanger Sequencing",1),("Pyro Sequecning",0);
                    """)

        pp.executescript("""
            CREATE TABLE status
                (id INTEGER PRIMARY KEY, status varchar(20));
            """)

        pp.executescript("""
            CREATE TABLE primers
                (id INTEGER PRIMARY KEY,
                alias varchar(20),
                sequence varchar(100),
                gene VARCHAR(20),
                chrom VARCHAR(2),
                position INTEGER,
                historial_alias VARCHAR(20),
                orientation integer(2),
                pair_id INTEGER,
                mod_5 varchar(20),
                mod_3 varchar(20),
                scale varchar(20),
                purification varchar(20),
                service varchar(20),
                date_designed varchar(20),
                user_designed INTEGER,
                date_checked varchar(20),
                user_checked INTEGER ,
                date_ordered VARCHAR(20),
                user_ordered INTEGER,
                lot_no varchar(20),
                date_received varchar(20),
                user_received INTEGER ,
                box_id INTEGER ,
                row INTEGER ,
                column INTEGER,
                date_reconstituted varchar(20),
                concentration INTEGER,
                user_reconstituted INTEGER,
                date_acceptance VARCHAR(20),
                worklist INTEGER,
                user_acceptance INTEGER,
                status INTEGER,
                current INTEGER,
                application INTEGER,
                FOREIGN KEY(pair_id) REFERENCES pairs(id),
                FOREIGN KEY(application) REFERENCES applications(id),
                FOREIGN KEY(user_ordered) REFERENCES users(id),
                FOREIGN KEY(user_received) REFERENCES users(id),
                FOREIGN KEY(box_id) REFERENCES boxes(id),
                FOREIGN KEY(user_reconstituted) REFERENCES users(id),
                FOREIGN KEY(user_checked) REFERENCES users(id),
                FOREIGN KEY(user_acceptance) REFERENCES users(id),
                FOREIGN KEY(status) REFERENCES status(id),
                FOREIGN KEY(user_designed) REFERENCES users(id));
            """)

        pp.executescript("""
            CREATE TABLE aliquots
                (id INTEGER PRIMARY KEY,
                primer_id INTEGER,
                box_id INTEGER,
                row INTEGER,
                column INTEGER,
                user_aliquoted INTEGER,
                date_aliquoted VARCHAR(20),
                FOREIGN KEY(user_aliquoted) REFERENCES users(id),
                FOREIGN KEY(primer_id) REFERENCES primers(id),
                FOREIGN KEY(box_id) REFERENCES boxes(id));
            """)

        pp.executescript("""
            CREATE TABLE pairs
                (id INTEGER PRIMARY KEY, forward INTEGER UNIQUE , reverse INTEGER UNIQUE, FOREIGN KEY(forward) REFERENCES primers(id),  FOREIGN KEY(reverse) REFERENCES primers(id));
            """)

        pp.executescript("""
            CREATE TABLE sets
                (id INTEGER PRIMARY KEY, name INTEGER, user INTEGER, date VARCHAR(20), current,  FOREIGN KEY(user) REFERENCES users(id));
            """)

        pp.executescript("""
            CREATE TABLE set_members
                (id INTEGER PRIMARY KEY, set_id INTEGER, primer_id INTEGER, user INTEGER , FOREIGN KEY(user) REFERENCES users(id),FOREIGN KEY(primer_id) REFERENCES primers(id),FOREIGN KEY(set_id) REFERENCES sets(id));
            """)

        pp.executescript("""
            CREATE TABLE saved_carts
                (id INTEGER PRIMARY KEY, name VARCHAR(20), user INTEGER, ids VARCHAR(255), date VARCHAR(20), FOREIGN KEY(user) REFERENCES users(id));
            """)

        pp.executescript("""
            CREATE TABLE conditions
                (id INTEGER PRIMARY KEY, pair_id INTEGER, FOREIGN KEY(pair_id) REFERENCES pairs(id));
            """)

        pp.executescript("""
            CREATE TABLE comments
                (id INTEGER PRIMARY KEY, primer_id INTEGER, pair_id INTEGER, user_id INTEGER, comment VARCHAR(1000),date VARCHAR(20), FOREIGN KEY(user_id) REFERENCES users(id),FOREIGN KEY(primer_id) REFERENCES primers(id), FOREIGN KEY(pair_id) REFERENCES pairs(id));
            """)


        pp.executescript("commit")
        return True
    except conn.Error as e:
        pp.executescript("rollback")
        print(e.args[0])
        return False


def main():
    parser = argparse.ArgumentParser(description='creates db tables required for primer program')
    parser.add_argument('--db')
    parser.add_argument('--users', default='dnamdp,cytng,gencph,genes,dnanhc')
    args = parser.parse_args()

    db = args.db
    print(db)

    conn_main = sqlite3.connect(db)
    complete = create_db(conn_main)
    u = Users()
    print complete
    if not complete:
        print "Database creation failed. Exiting."
        exit()
    if args.users is not None:
        users = args.users.split(',')
        for user in users:
            print user
            complete = u.add_user(user, 1)
            print complete
            if complete == -1:
                print user + " not added to database"


if __name__ == '__main__':
    main()
