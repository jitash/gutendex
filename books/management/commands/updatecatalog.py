from subprocess import call
import json
import os
import shutil
from time import strftime, sleep
import sys
import urllib.request
import urllib.error

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError

from books import utils
from books.models import *


def sync_directories(source_dir, target_dir, delete_after=True):
    """
    使用 Python 同步目录，替代 rsync 命令
    功能：将 source_dir 的内容同步到 target_dir
    
    Args:
        source_dir: 源目录路径
        target_dir: 目标目录路径
        delete_after: 是否删除目标目录中源目录不存在的文件
    """
    if not os.path.exists(source_dir):
        raise CommandError(f'Source directory does not exist: {source_dir}')
    
    # 确保目标目录存在
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # 获取源目录和目标目录中的所有文件和目录
    source_items = set()
    target_items = set()
    
    # 获取源目录中的项目
    for item in os.listdir(source_dir):
        source_items.add(item)
    
    # 获取目标目录中的项目
    if os.path.exists(target_dir):
        for item in os.listdir(target_dir):
            target_items.add(item)
    
    # 如果需要删除目标目录中不存在的文件
    if delete_after:
        items_to_delete = target_items - source_items
        for item in items_to_delete:
            item_path = os.path.join(target_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
    
    # 复制/更新源目录的文件和目录到目标目录
    for item in source_items:
        source_path = os.path.join(source_dir, item)
        target_path = os.path.join(target_dir, item)
        
        if os.path.isdir(source_path):
            # 如果是目录，递归复制
            if os.path.exists(target_path):
                # 如果目标目录已存在，先删除
                shutil.rmtree(target_path)
            shutil.copytree(source_path, target_path)
        else:
            # 如果是文件，直接复制
            if os.path.exists(target_path):
                os.remove(target_path)
            shutil.copy2(source_path, target_path)


TEMP_PATH = settings.CATALOG_TEMP_DIR

URL = 'https://gutenberg.org/cache/epub/feeds/rdf-files.tar.bz2'
DOWNLOAD_PATH = os.path.join(TEMP_PATH, 'catalog.tar.bz2')

MOVE_SOURCE_PATH = os.path.join(TEMP_PATH, 'cache/epub')
MOVE_TARGET_PATH = settings.CATALOG_RDF_DIR

LOG_DIRECTORY = settings.CATALOG_LOG_DIR
LOG_FILE_NAME = strftime('%Y-%m-%d_%H%M%S') + '.txt'
LOG_PATH = os.path.join(LOG_DIRECTORY, LOG_FILE_NAME)


# This gives a set of the names of the subdirectories in the given file path.
def get_directory_set(path):
    directory_set = set()
    for directory_item in os.listdir(path):
        item_path = os.path.join(path, directory_item)
        if os.path.isdir(item_path):
            directory_set.add(directory_item)
    return directory_set


def log(*args):
    print(*args)
    if not os.path.exists(LOG_DIRECTORY):
        os.makedirs(LOG_DIRECTORY)
    with open(LOG_PATH, 'a') as log_file:
        text = ' '.join(args) + '\n'
        log_file.write(text)


def put_catalog_in_db():
    book_ids = []
    for directory_item in os.listdir(settings.CATALOG_RDF_DIR):
        item_path = os.path.join(settings.CATALOG_RDF_DIR, directory_item)
        if os.path.isdir(item_path):
            try:
                book_id = int(directory_item)
            except ValueError:
                # Ignore the item if it's not a book ID number.
                pass
            else:
                book_ids.append(book_id)
    book_ids.sort()
    book_directories = [str(id) for id in book_ids]

    for directory in book_directories:
        id = int(directory)

        if (id > 0) and (id % 500 == 0):
            log('    %d' % id)

        book_path = os.path.join(
            settings.CATALOG_RDF_DIR,
            directory,
            'pg' + directory + '.rdf'
        )

        book = utils.get_book(id, book_path)

        try:
            '''Make/update the book.'''

            book_in_db = Book.objects.filter(gutenberg_id=id)

            if book_in_db.exists():
                book_in_db = book_in_db[0]
                book_in_db.copyright = book['copyright']
                book_in_db.download_count = book['downloads']
                book_in_db.media_type = book['type']
                book_in_db.title = book['title']
                book_in_db.save()
            else:
                book_in_db = Book.objects.create(
                    gutenberg_id=id,
                    copyright=book['copyright'],
                    download_count=book['downloads'],
                    media_type=book['type'],
                    title=book['title']
                )

            ''' Make/update the authors. '''

            authors = []
            for author in book['authors']:
                person = get_or_create_person(author)
                authors.append(person)

            book_in_db.authors.clear()
            for author in authors:
                book_in_db.authors.add(author)

            ''' Make/update the editors. '''

            editors = []
            for editor in book['editors']:
                person = get_or_create_person(editor)
                editors.append(person)

            book_in_db.editors.clear()
            for editor in editors:
                book_in_db.editors.add(editor)

            ''' Make/update the translators. '''

            translators = []
            for translator in book['translators']:
                person = get_or_create_person(translator)
                translators.append(person)

            book_in_db.translators.clear()
            for translator in translators:
                book_in_db.translators.add(translator)

            ''' Make/update the book shelves. '''

            bookshelves = []
            for shelf in book['bookshelves']:
                shelf_in_db = Bookshelf.objects.filter(name=shelf)
                if shelf_in_db.exists():
                    shelf_in_db = shelf_in_db[0]
                else:
                    shelf_in_db = Bookshelf.objects.create(name=shelf)
                bookshelves.append(shelf_in_db)

            book_in_db.bookshelves.clear()
            for bookshelf in bookshelves:
                book_in_db.bookshelves.add(bookshelf)

            ''' Make/update the formats. '''

            old_formats = Format.objects.filter(book=book_in_db)

            format_ids = []
            for format_ in book['formats']:
                format_in_db = Format.objects.filter(
                    book=book_in_db,
                    mime_type=format_,
                    url=book['formats'][format_]
                )
                if format_in_db.exists():
                    format_in_db = format_in_db[0]
                else:
                    format_in_db = Format.objects.create(
                        book=book_in_db,
                        mime_type=format_,
                        url=book['formats'][format_]
                    )
                format_ids.append(format_in_db.id)

            for old_format in old_formats:
                if old_format.id not in format_ids:
                    old_format.delete()

            ''' Make/update the languages. '''

            languages = []
            for language in book['languages']:
                language_in_db = Language.objects.filter(code=language)
                if language_in_db.exists():
                    language_in_db = language_in_db[0]
                else:
                    language_in_db = Language.objects.create(code=language)
                languages.append(language_in_db)

            book_in_db.languages.clear()
            for language in languages:
                book_in_db.languages.add(language)

            ''' Make/update subjects. '''

            subjects = []
            for subject in book['subjects']:
                subject_in_db = Subject.objects.filter(name=subject)
                if subject_in_db.exists():
                    subject_in_db = subject_in_db[0]
                else:
                    subject_in_db = Subject.objects.create(name=subject)
                subjects.append(subject_in_db)

            book_in_db.subjects.clear()
            for subject in subjects:
                book_in_db.subjects.add(subject)

            ''' Make/update summaries. '''

            old_summaries = Summary.objects.filter(book=book_in_db)

            summary_ids = []
            for summary in book['summaries']:
                summary_in_db = Summary.objects.filter(book=book_in_db, text=summary)
                if summary_in_db.exists():
                    summary_in_db = summary_in_db[0]
                else:
                    summary_in_db = Summary.objects.create(
                        book=book_in_db, text=summary
                    ) 
                summary_ids.append(summary_in_db.id)

            for old_summary in old_summaries:
                if old_summary.id not in summary_ids:
                    old_summary.delete()

        except Exception as error:
            book_json = json.dumps(book, indent=4)
            log(
                '  Error while putting this book info in the database:\n',
                book_json,
                '\n'
            )
            raise error


def get_or_create_person(data):
    person = Person.objects.filter(
        name=data['name'],
        birth_year=data['birth'],
        death_year=data['death']
    )

    if person.exists():
        person = person[0]
    else:
        person = Person.objects.create(
            name=data['name'],
            birth_year=data['birth'],
            death_year=data['death']
        )
    
    return person


def send_log_email():
    if not (settings.ADMIN_EMAILS or settings.EMAIL_HOST_ADDRESS):
        return

    log_text = ''
    with open(LOG_PATH, 'r') as log_file:
        log_text = log_file.read()

    email_html = '''
        <h1 style="color: #333;
                   font-family: 'Helvetica Neue', sans-serif;
                   font-size: 64px;
                   font-weight: 100;
                   text-align: center;">
            Gutendex
        </h1>

        <p style="color: #333;
                  font-family: 'Helvetica Neue', sans-serif;
                  font-size: 24px;
                  font-weight: 200;">
            Here is the log from your catalog retrieval:
        </p>

        <pre style="color:#333;
                    font-family: monospace;
                    font-size: 16px;
                    margin-left: 32px">''' + log_text + '</pre>'

    email_text = '''GUTENDEX

    Here is the log from your catalog retrieval:

    ''' + log_text

    send_mail(
        subject='Catalog retrieval',
        message=email_text,
        html_message=email_html,
        from_email=settings.EMAIL_HOST_ADDRESS,
        recipient_list=settings.ADMIN_EMAILS
    )


class Command(BaseCommand):
    help = 'This replaces the catalog files with the latest ones.'

    def handle(self, *args, **options):
        try:
            date_and_time = strftime('%H:%M:%S on %B %d, %Y')
            log('Starting script at', date_and_time)

            log('  Making temporary directory...')
            if os.path.exists(TEMP_PATH):
                raise CommandError(
                    'The temporary path, `' + TEMP_PATH + '`, already exists.'
                )
            else:
                os.makedirs(TEMP_PATH)

            log('  Downloading compressed catalog...')
            # 添加重试机制下载文件
            max_retries = 5
            retry_delay = 10  # 秒
            downloaded = False
            
            for attempt in range(1, max_retries + 1):
                try:
                    log(f'    Attempt {attempt}/{max_retries}...')
                    # 如果文件已存在但可能不完整，先删除
                    if os.path.exists(DOWNLOAD_PATH):
                        file_size = os.path.getsize(DOWNLOAD_PATH)
                        # 如果文件很小（小于1MB），可能是之前失败的部分下载，删除它
                        if file_size < 1024 * 1024:  # 1MB
                            os.remove(DOWNLOAD_PATH)
                            log(f'    Removed incomplete download ({file_size} bytes)')
                    
                    # 下载文件
                    urllib.request.urlretrieve(URL, DOWNLOAD_PATH)
                    
                    # 验证下载的文件大小（至少应该大于某个阈值）
                    if os.path.exists(DOWNLOAD_PATH):
                        file_size = os.path.getsize(DOWNLOAD_PATH)
                        # Project Gutenberg RDF 文件通常大于 100MB
                        if file_size > 100 * 1024 * 1024:  # 100MB
                            downloaded = True
                            log(f'    Download completed: {file_size / (1024*1024):.2f} MB')
                            break
                        else:
                            log(f'    Downloaded file too small ({file_size / (1024*1024):.2f} MB), may be incomplete')
                            if attempt < max_retries:
                                os.remove(DOWNLOAD_PATH)
                                log(f'    Retrying in {retry_delay} seconds...')
                                sleep(retry_delay)
                    
                except (urllib.error.URLError, IOError, OSError) as e:
                    error_msg = str(e)
                    log(f'    Download attempt {attempt} failed: {error_msg}')
                    
                    # 删除可能的不完整文件
                    if os.path.exists(DOWNLOAD_PATH):
                        try:
                            os.remove(DOWNLOAD_PATH)
                        except:
                            pass
                    
                    if attempt < max_retries:
                        log(f'    Retrying in {retry_delay} seconds...')
                        sleep(retry_delay)
                    else:
                        raise CommandError(f'Failed to download catalog after {max_retries} attempts: {error_msg}')
            
            if not downloaded:
                raise CommandError('Failed to download catalog file')

            log('  Decompressing catalog...')
            if not os.path.exists(DOWNLOAD_PATH):
                os.makedirs(DOWNLOAD_PATH)
            with open(os.devnull, 'w') as null:
                call(
                    ['tar', 'fjvx', DOWNLOAD_PATH, '-C', TEMP_PATH],
                    stdout=null,
                    stderr=null
                )

            log('  Detecting stale directories...')
            if not os.path.exists(MOVE_TARGET_PATH):
                os.makedirs(MOVE_TARGET_PATH)
            new_directory_set = get_directory_set(MOVE_SOURCE_PATH)
            old_directory_set = get_directory_set(MOVE_TARGET_PATH)
            stale_directory_set = old_directory_set - new_directory_set

            log('  Removing stale directories and books...')
            for directory in stale_directory_set:
                try:
                    book_id = int(directory)
                except ValueError:
                    # Ignore the directory if its name isn't a book ID number.
                    continue
                book = Book.objects.filter(gutenberg_id=book_id)
                book.delete()
                path = os.path.join(MOVE_TARGET_PATH, directory)
                shutil.rmtree(path)

            log('  Replacing old catalog files...')
            try:
                # 使用 Python 同步目录，替代 rsync（因为容器中可能没有 rsync）
                sync_directories(MOVE_SOURCE_PATH, MOVE_TARGET_PATH, delete_after=True)
            except Exception as e:
                # 如果同步失败，记录错误但不中断流程
                error_msg = f'Error syncing directories: {str(e)}'
                log(error_msg)
                # 仍然尝试继续处理，使用简单的复制方法作为后备
                if os.path.exists(MOVE_SOURCE_PATH):
                    # 如果目标目录存在，先清空它
                    if os.path.exists(MOVE_TARGET_PATH):
                        shutil.rmtree(MOVE_TARGET_PATH)
                    # 复制整个目录
                    shutil.copytree(MOVE_SOURCE_PATH, MOVE_TARGET_PATH)

            log('  Putting the catalog in the database...')
            put_catalog_in_db()

            log('  Removing temporary files...')
            shutil.rmtree(TEMP_PATH)

            log('Done!\n')
        except Exception as error:
            error_message = str(error)
            log('Error:', error_message)
            log('')
            shutil.rmtree(TEMP_PATH)

        send_log_email()
