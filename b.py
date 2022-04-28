import click
import sys
'''
'''
@click.command()
@click.option('--count', default=1, help='number of greetings')
@click.argument('name')
def hello(count, name):
    print(count)
    for x in range(count):
        click.echo('Hello %s!' % name)



print(sys.argv)
hello()