from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.urls import reverse

class User(AbstractUser):
    # extend the build-in django user model by adding phone and user account date created
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Business(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='businesses')
    name = models.CharField(max_length=200)
    address = models.TextField()
    google_review_url = models.URLField(help_text="Direct link to Google Reviews page")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    def get_review_link(self):
        """Get or create the main review link for this business"""
        link, created = ReviewLink.objects.get_or_create(
            business=self,
            defaults={'token': str(uuid.uuid4())}
        )
        return link
    
    class Meta:
        verbose_name_plural = "businesses"

class ReviewLink(models.Model):
    """Unique link that customers use to submit reviews"""
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='review_link')
    token = models.UUIDField(default=uuid.uuid4, unique=True) # create a unique id
    click_count = models.PositiveIntegerField(default=0) # Tracks how many times this review link has been clicked
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"Review link for {self.business.name}"
    
    def get_absolute_url(self):
        return reverse('reviews:review_form', kwargs={'token': self.token})
        # this function triggers urls.py /review/ and returns something like "/review/abc123-def456-ghi789/"
    
    def increment_clicks(self):
        self.click_count += 1
        self.save(update_fields=['click_count'])


class CustomerReview(models.Model):
    """Individual review submitted by a customer"""
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('redirected', 'Redirected to Google'),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reviews')
    review_link = models.ForeignKey(ReviewLink, on_delete=models.CASCADE, related_name='reviews')
    
    # Customer input
    customer_name = models.CharField(max_length=100, blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    feedback = models.TextField(help_text="What did you like about your experience?")
    
    # AI generated content
    ai_review = models.TextField(blank=True, help_text="AI-generated review based on feedback")
    
    # Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.rating}★ review for {self.business.name}"
    

    # 
    def generate_ai_review(self):
        """Generate AI review based on rating and feedback"""
        # back up template in case ai assistance don't work
        if self.rating >= 4:
            templates = [
                f"Had a wonderful experience at {self.business.name}! {self.feedback} Definitely recommend this place.",
                f"Really enjoyed my visit to {self.business.name}. {self.feedback} Will be coming back!",
                f"Great place! {self.feedback} {self.business.name} exceeded my expectations."
            ]
        elif self.rating == 3:
            templates = [
                f"Decent experience at {self.business.name}. {self.feedback}",
                f"Overall okay visit to {self.business.name}. {self.feedback}"
            ]
        else:
            templates = [
                f"Visited {self.business.name}. {self.feedback}",
            ]
        
        import random
        self.ai_review = random.choice(templates)
        self.save(update_fields=['ai_review'])
        return self.ai_review
    
    class Meta:
        ordering = ['-created_at']