#!/usr/bin/env python
# This script is needed for gitlab CI
# It waits until postgres is up and ready to process queries

import time
import psycopg2
import argparse
import os
import abc

parser = argparse.ArgumentParser(description='CLI tool for waiting postgres')
parser.add_argument('--port', type=int, default=5432,
                    help='port to connect')
parser.add_argument('--host', default='localhost',
                    help='host to connect')

parser.add_argument('--db', default='postgresa
                    help='db to connect')

parser.add_argument('--user', default='postgres',
                    help='postgres user to connect as')

parser.add_argument('--password', default='',
                    help='postgres password to connect with')


parser.add_argument('--delay', default=2, type=int,
                    help='time to wait before reconnect')

args = parser.parse_args()


class ServiceWaiter(abc.ABC):

    @abc.abstractmethod
    def wait(self):
        raise NotImplementedError


class PostgresServiceWaiter(ServiceWaiter):

    def __init__(self, host, user, password, dbname, port=5432, delay=3):
        self.host = host
        self.user = user
        self.password = password
        self.dbname = dbname
        self.port = port
        self.delay = delay

    def __is_service_ready(self):
        c = None
        conn = None
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                dbname=self.dbname,
                password=self.password
            )
            c = conn.cursor()
            c.execute('SELECT 1')
            c.fetchone()
        except psycopg2.OperationalError as e:
            print(e)
            return False
        finally:
            if c is not None:
                c.close()
            if conn is not None:
                conn.close()
        return True

    def wait(self):
        while True:
            pg_ready = self.__is_service_ready()
            if pg_ready:
                print(f'!!Postgres is ready!!')
                break
            else:
                print(f'Postgres is not ready! Reconnecting in {self.delay}..')
                time.sleep(self.delay)


if __name__ == '__main__':
    host = os.environ.get('POSTGRES_HOST', args.host)
    port = os.environ.get('POSTGRES_PORT', args.port)
    user = os.environ.get('POSTGRES_USER', args.user)
    db = os.environ.get('POSTGRES_DB', args.db)
    password = os.environ.get('POSTGRES_PASSWORD', args.password)
    delay = args.delay

    msg = "Connection info:\n"
    msg += "-------------------------------\n"
    msg += f"host: {host}\n"
    msg += f"port: {port}\n"
    msg += f"user: {user}\n"
    msg += f"db: {db}\n"
    msg += f"delay: {delay}\n"
    msg += "-------------------------------"
    print(msg)
    print(f'Trying to connect {host}:{port}..')
    postgres_service = PostgresServiceWaiter(
        host=host,
        port=port,
        user=user,
        dbname=db,
        password=password,
        delay=delay
    )
    postgres_service.wait()
