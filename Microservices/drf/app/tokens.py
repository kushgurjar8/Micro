from rest_framework_simplejwt.tokens import RefreshToken

class MyToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)        
        token['username'] = user.username  
        token['email'] = user.email
        token['first_name'] = user.first_name
        return token