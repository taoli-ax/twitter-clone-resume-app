from tweets.models import TweetPhoto


class TweetPhotoService:
    @classmethod
    def create_tweet_photo(cls, tweet, files):
        photos = []
        for index, file in enumerate(files):
            photo = TweetPhoto(
                tweet=tweet,
                user=tweet.user,
                file=file,
                order=index
            )
            photos.append(photo)
        TweetPhoto.objects.bulk_create(photos)