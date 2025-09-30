from django.db import models
import uuid
from django.urls import reverse
from users.models import User

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
        """Get or create the review link for this business

        link: the reviewlink instance (existing one or new)
        created: True (just created) / False (already exists)
        """
        link, created = ReviewLink.objects.get_or_create( # Query/Create (SELECT OR INSERT)
            business=self,
            defaults={'token': str(uuid.uuid4())} # if link doesn't exist, create fresh uUUID
        )
        return link
    
    # display businesses instead of business in django admin
    class Meta:
        verbose_name_plural = "businesses"

class ReviewLink(models.Model):
    """
    Unique link that customers use to submit reviews
    """
    business = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='review_link')
    token = models.UUIDField(default=uuid.uuid4, unique=True) # create a unique id
    click_count = models.PositiveIntegerField(default=0) # Tracks how many times this review link has been clicked

    def __str__(self):
        return f"Review link for {self.business.name}"
    
    def get_absolute_url(self):
        return reverse('reviews:review_form', kwargs={'token': self.token})
    # this function triggers urls.py /review/ and returns something like "/review/abc123-def456-ghi789/"
    
    def increment_clicks(self):
        self.click_count += 1
        self.save()

class CustomerReview(models.Model):
    """Individual review submitted by a customer"""
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='reviews')
    review_link = models.ForeignKey(ReviewLink, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    feedback = models.TextField(help_text="What did you like about your experience?")
    ai_review = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.rating}★ review for {self.business.name}"
    
    class Meta:
        ordering = ['-created_at']