# ShopSmart - AI-Powered E-Commerce

Django e-commerce application with AI-powered product recommendations and Cython optimization.

## Technologies

- Django 5.0.6
- Python 3.12
- NumPy (Collaborative Filtering)
- Cython (Performance Optimization)
- SQLite

## How It Works

**The AI Recommendation Engine:**
We use collaborative filtering to recommend products - basically, the app learns from user behavior. When you browse products, add items to cart or click like/dislike, the system tracks these interactions. It then builds a similarity matrix that figures out which products are similar to each other based on what users interact with.

Users who liked similar products to what you liked will influence what gets recommended to you. It's like having a smart shopping buddy who knows your taste.

**The Cython Optimization:**
Here's where we made things fast - the similarity calculations (comparing all products against each other) can get really slow with lots of products. So we wrote the heavy math parts in Cython, which compiles to C code and runs way faster than pure Python. Specifically, we optimized:
- Computing the similarity matrix using cosine similarity
- Predicting user scores for products

This means recommendations load quickly even as the product catalog grows.

## How to Run

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Build Cython extensions:
```bash
python setup.py build_ext --inplace
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create sample data (includes users):
```bash
python manage.py populate_data
```

5. Start server:
```bash
python manage.py runserver
```

6. Access at: http://localhost:8000/

## Login Credentials

**Regular User:**
- Username: user
- Password: user123

**Admin User:**
- Username: admin
- Password: admin123
- Admin Panel: http://localhost:8000/admin/

## Features

- Browse products by category
- View personalized product recommendations
- Like/dislike products to improve recommendations
- Shopping cart with quantity management
- Complete checkout process
- Order history tracking
- AI learns from your interactions in real-time
