"""Модульні тести для CRUD операцій з постами"""
import unittest
from datetime import datetime
from app import create_app, db
from app.posts.models import Post
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



    def test_create_post_get(self):
        """Тест 1: GET запит до форми створення поста повертає статус 200"""
        response = self.client.get('/post/create')
        response_text = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
    
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
  
            stmt = select(Post).where(Post.title == 'New Test Post')

            post = db.session.scalar(stmt)
            
            self.assertIsNotNone(post)
            self.assertEqual(post.content, 'This is test content for new post')
            self.assertEqual(post.category, 'tech')
            self.assertEqual(post.author, 'Anonymous')

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
        
        data = {
            'title': 'Updated Title',
            'content': 'Updated content here',
            'category': 'tech',
            'enabled': True,
            'publish_date': datetime.utcnow().strftime('%Y-%m-%dT%H:%M'),
            'submit': True
        }
        
        response = self.client.post(f'/post/{post_id}/update', data=data, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        
        with self.app.app_context():
            post = db.session.get(Post, post_id)
            
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
        self.assertIn('To Delete', response_text)
    
    def test_delete_post_post_success(self):
        """Тест 2: POST запит видаляє пост і перенаправляє"""
        post_id = self._create_test_post(title="Will Be Deleted", content="Delete me")
        
        response = self.client.post(f'/post/{post_id}/delete', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        
        with self.app.app_context():
            post = db.session.get(Post, post_id)
            
            self.assertIsNone(post)


if __name__ == "__main__":
    unittest.main()