"""Модульні тести для CRUD операцій з постами"""
import unittest
from datetime import datetime
from app import create_app, db
from app.posts.models import Post
from app.models import User
from sqlalchemy import select  

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
            # Створюємо тестового користувача та зберігаємо його ID
            user = self._create_test_user()
            self.test_user_id = user.id
            # Expunge об'єкт, щоб уникнути проблем з сесією
            db.session.expunge(user)
    
    def tearDown(self):
        """Очищення після кожного тесту"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def _create_test_user(self, username="TestUser", email="test@example.com", password="testpass"):
        """Допоміжний метод для створення тестового користувача"""
        user = User(
            username=username,
            email=email,
            password=password
        )
        db.session.add(user)
        db.session.commit()
        return user
    
    def _create_test_post(self, title="Test Post", content="Test content", is_active=True, user_id=None, category='news'):
        """Допоміжний метод для створення тестового поста"""
        with self.app.app_context():
            if user_id is None:
                user_id = self.test_user_id
            post = Post(
                title=title,
                content=content,
                is_active=is_active,
                posted=datetime.utcnow(),
                category=category,
                user_id=user_id
            )
            db.session.add(post)
            db.session.commit()
            return post.id



    def test_create_post_get(self):
        """Тест 1: GET запит до форми створення поста повертає статус 200"""
        response = self.client.get('/post/create')
        response_text = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
    
        self.assertIn('Заголовок', response_text)
    
    def test_create_post_post_success(self):
        """Тест 2: POST запит створює новий пост і перенаправляє"""
        with self.app.app_context():
            data = {
                'title': 'New Test Post',
                'content': 'This is test content for new post',
                'category': 'tech',
                'author_id': self.test_user_id,
                'enabled': True,
                'publish_date': datetime.utcnow().strftime('%Y-%m-%dT%H:%M'),
                'submit': True
            }
            
            response = self.client.post('/post/create', data=data, follow_redirects=False)
            self.assertEqual(response.status_code, 302)  # Redirect після створення
            
            # Перевіряємо, що пост створено
            stmt = select(Post).where(Post.title == 'New Test Post')
            post = db.session.scalar(stmt)
            
            self.assertIsNotNone(post)
            self.assertEqual(post.content, 'This is test content for new post')
            self.assertEqual(post.category, 'tech')
            self.assertEqual(post.user_id, self.test_user_id)
            self.assertIsNotNone(post.user)
            self.assertEqual(post.user.username, 'TestUser')

    # Тести для /post/<int:id>/update (update_post)
    def test_update_post_get(self):
        """Тест 1: GET запит до форми редагування повертає статус 200"""
        post_id = self._create_test_post(title="Original Title", content="Original content")
        
        response = self.client.get(f'/post/{post_id}/update')
        response_text = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Original Title', response_text)
        self.assertIn('Original content', response_text)
    
    def test_update_post_post_success(self):
        """Тест 2: POST запит оновлює пост і перенаправляє"""
        post_id = self._create_test_post(title="Old Title", content="Old content", category='news')
        
        with self.app.app_context():
            data = {
                'title': 'Updated Title',
                'content': 'Updated content here',
                'category': 'tech',
                'author_id': self.test_user_id,
                'enabled': True,
                'publish_date': datetime.utcnow().strftime('%Y-%m-%dT%H:%M'),
                'submit': True
            }
            
            response = self.client.post(f'/post/{post_id}/update', data=data, follow_redirects=False)
            self.assertEqual(response.status_code, 302)
            
            post = db.session.get(Post, post_id)
            
            self.assertEqual(post.title, 'Updated Title')
            self.assertEqual(post.content, 'Updated content here')
            self.assertEqual(post.category, 'tech')
            self.assertEqual(post.user_id, self.test_user_id)

    # Тести для /post/<int:id>/delete (delete_post)
    def test_delete_post_get(self):
        """Тест 1: GET запит до сторінки підтвердження видалення повертає статус 200"""
        post_id = self._create_test_post(title="To Delete", content="Will be deleted")
        
        response = self.client.get(f'/post/{post_id}/delete')
        response_text = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('To Delete', response_text)
    
    def test_delete_post_post_success(self):
        """Тест 2: POST запит видаляє пост і перенаправляє"""
        post_id = self._create_test_post(title="Will Be Deleted", content="Delete me")
        
        response = self.client.post(f'/post/{post_id}/delete', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        
        with self.app.app_context():
            post = db.session.get(Post, post_id)
            
            self.assertIsNone(post)

    # Тести для /post (posts_list)
    def test_posts_list(self):
        """Тест: GET запит до списку постів повертає статус 200 і відображає пости"""
        self._create_test_post(title="Post 1", content="Content 1", is_active=True)
        self._create_test_post(title="Post 2", content="Content 2", is_active=True)
        self._create_test_post(title="Inactive Post", content="Content 3", is_active=False)
        
        response = self.client.get('/post')
        response_text = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Post 1', response_text)
        self.assertIn('Post 2', response_text)
        self.assertNotIn('Inactive Post', response_text)  # Неактивні пости не відображаються
        self.assertIn('TestUser', response_text)  # Перевіряємо, що автор відображається

    # Тести для /post/<int:id> (post_detail)
    def test_post_detail(self):
        """Тест: GET запит до деталей поста повертає статус 200 і відображає автора"""
        post_id = self._create_test_post(title="Detail Post", content="Detail content")
        
        response = self.client.get(f'/post/{post_id}')
        response_text = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Detail Post', response_text)
        self.assertIn('Detail content', response_text)
        self.assertIn('TestUser', response_text)  # Перевіряємо, що автор відображається

    def test_post_detail_inactive(self):
        """Тест: GET запит до неактивного поста перенаправляє на список"""
        post_id = self._create_test_post(title="Inactive Post", content="Content", is_active=False)
        
        response = self.client.get(f'/post/{post_id}', follow_redirects=False)
        self.assertEqual(response.status_code, 302)  # Redirect до списку постів


if __name__ == "__main__":
    unittest.main()