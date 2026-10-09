"""Narrow OWN-scope regression using synthetic CI accounts only."""
import secrets,time,urllib.error

def run_rbac(req,owner_token,group_id):
    own={'scope':1}
    role=req('POST','/api/admin-role',{'name':'sabi-ci-own','permissions':{'users':{'create':own,'read':own,'read_simple':own,'update':own,'delete':own},'groups':{'read_simple':True}},'access':{'allowed_group_ids':[group_id]}},owner_token)
    tokens=[]
    for name in ['sabi_ci_a','sabi_ci_b']:
        password='Ci-'+secrets.token_hex(18)+'-Aa9!'
        req('POST','/api/admin',{'username':name,'password':password,'role_id':role['id']},owner_token)
        token=req('POST','/api/admin/token',{'username':name,'password':password},form=True)['access_token']
        req('POST','/api/user',{'username':name+'_user','group_ids':[group_id],'status':'active','data_limit':1048576,'expire':int(time.time())+86400},token)
        tokens.append(token)
    for index,token in enumerate(tokens):
        own_name=['sabi_ci_a_user','sabi_ci_b_user'][index];other=['sabi_ci_b_user','sabi_ci_a_user'][index]
        assert req('GET','/api/user/'+own_name,token=token)['username']==own_name
        visible=req('GET','/api/users?limit=100',token=token)
        assert all(u['username']!=other for u in visible['users'])
        for method,path,body in [('GET','/api/user/'+other,None),('PUT','/api/user/'+other,{'note':'should-not-apply'}),('DELETE','/api/user/'+other,None),('GET','/api/cores',None)]:
            try:req(method,path,body,token)
            except urllib.error.HTTPError as e:assert e.code in (403,404)
            else:raise AssertionError('Cross-scope access unexpectedly allowed')
    print('PASS: OWN-scope resellers cannot read/update/delete another reseller user or read cores; own-user read works.')
