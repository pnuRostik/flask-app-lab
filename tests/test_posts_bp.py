"""Модульні тести для CRUD операцій з постами"""
import unittest
from datetime import datetime
from app import create_app, db
from app.posts.models import Post


class PostsTestCase(unittest.TestCase):
    """Тести для ендпоінтів posts"""

    def setUp(self):
        """Налаштування перед кожним тестом"""
        self.app = create_app('test')
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Вимкнути CSRF для тестів
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Очищення після кожного тесту"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def _create_test_post(self, title="Test Post", content="Test content", is_active=True, author="TestUser", category='news'):
        """Допоміжний метод для створення тестового поста"""
        with self.app.app_context():
            post = Post(
                title=title,
                content=content,
                is_active=is_active,
                posted=datetime.utcnow(),
                category=category,
                author=author
            )
            db.session.add(post)
            db.session.commit()
            return post.id

    # Тести для /post (posts_list)
    def test_posts_list_get(self):
        """Тест 1: GET запит до списку постів повертає статус 200"""
        response = self.client.get('/post')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Список постів', response.get_data(as_text=True))
    
    def test_posts_list_shows_only_active(self):
        """Тест 2: Список постів показує тільки активні пости"""
        # Створюємо активний та неактивний пост
        active_id = self._create_test_post(title="Active Post", is_active=True)
        inactive_id = self._create_test_post(title="Inactive Post", is_active=False)
        
        response = self.client.get('/post')
        response_text = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Active Post', response_text)
        self.assertNotIn('Inactive Post', response_text)

    # Тести для /post/<int:id> (post_detail)
    def test_post_detail_get(self):
        """Тест 1: GET запит до деталей поста повертає статус 200"""
        post_id = self._create_test_post(title="Detail Post", content="Detail content")
        
        response = self.client.get(f'/post/{post_id}')
        response_text = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Detail Post', response_text)
        self.assertIn('Detail content', response_text)
    
    def test_post_detail_inactive_redirects(self):
        """Тест 2: Перегляд неактивного поста перенаправляє на список"""
        post_id = self._create_test_post(title="Inactive", is_active=False)
        
        response = self.client.get(f'/post/{post_id}', follow_redirects=False)
        self.assertEqual(response.status_code, 302)  # Redirect

    # Тести для /post/create (create_post)
    def test_create_post_get(self):
        """Тест 1: GET запит до форми створення поста повертає статус 200"""
        response = self.client.get('/post/create')
        response_text = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Додати новий пост', response_text)
        self.assertIn('Заголовок', response_text)
    
    def test_create_post_post_success(self):
        """Тест 2: POST запит створює новий пост і перенаправляє"""
        data = {
            'title': 'New Test Post',
            'content': 'This is test content for new post',
            'category': 'tech',
            'enabled': True,
            'publish_date': datetime.utcnow().strftime('%Y-%m-%dT%H:%M'),
            'submit': True
        }
        
        response = self.client.post('/post/create', data=data, follow_redirects=False)
        self.assertEqual(response.status_code, 302)  # Redirect після створення
        
        # Перевіряємо, що пост створено
        with self.app.app_context():
            post = Post.query.filter_by(title='New Test Post').first()
            self.assertIsNotNone(post)
            self.assertEqual(post.content, 'This is test content for new post')
            self.assertEqual(post.category, 'tech')
            self.assertEqual(post.author, 'Anonymous')  # Без сесії автор = Anonymous

    # Тести для /post/<int:id>/update (update_post)
    def test_update_post_get(self):
        """Тест 1: GET запит до форми редагування повертає статус 200"""
        post_id = self._create_test_post(title="Original Title", content="Original content")
        
        response = self.client.get(f'/post/{post_id}/update')
        response_text = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Редагувати пост', response_text)
        self.assertIn('Original Title', response_text)
        self.assertIn('Original content', response_text)
    
    def test_update_post_post_success(self):
        """Тест 2: POST запит оновлює пост і перенаправляє"""
        post_id = self._create_test_post(title="Old Title", content="Old content", category='news')
        
        data = {
            'title': 'Updated Title',
            'content': 'Updated content here',
            'category': 'tech',
            'enabled': True,
            'publish_date': datetime.utcnow().strftime('%Y-%m-%dT%H:%M'),
            'submit': True
        }
        
        response = self.client.post(f'/post/{post_id}/update', data=data, follow_redirects=False)
        self.assertEqual(response.status_code, 302)  # Redirect після оновлення
        
        # Перевіряємо, що пост оновлено
        with self.app.app_context():
            post = Post.query.get(post_id)
            self.assertEqual(post.title, 'Updated Title')
            self.assertEqual(post.content, 'Updated content here')
            self.assertEqual(post.category, 'tech')

    # Тести для /post/<int:id>/delete (delete_post)
    def test_delete_post_get(self):
        """Тест 1: GET запит до сторінки підтвердження видалення повертає статус 200"""
        post_id = self._create_test_post(title="To Delete", content="Will be deleted")
        
        response = self.client.get(f'/post/{post_id}/delete')
        response_text = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Підтвердження видалення', response_text)
        self.assertIn('To Delete', response_text)
    
    def test_delete_post_post_success(self):
        """Тест 2: POST запит видаляє пост і перенаправляє"""
        post_id = self._create_test_post(title="Will Be Deleted", content="Delete me")
        
        response = self.client.post(f'/post/{post_id}/delete', follow_redirects=False)
        self.assertEqual(response.status_code, 302)  # Redirect після видалення
        
        # Перевіряємо, що пост видалено
        with self.app.app_context():
            post = Post.query.get(post_id)
            self.assertIsNone(post)


if __name__ == "__main__":
    unittest.main()

