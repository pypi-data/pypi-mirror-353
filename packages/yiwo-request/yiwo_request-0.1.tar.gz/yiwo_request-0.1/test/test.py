
if __name__ == '__main__':
    from com.yiwo.yiwo_request import Reqeust
    request = Reqeust('uat', 'https://api.yiwo.com', '')
    result = request.get('/api/v1/user/getUserInfo', {})
    print(result)