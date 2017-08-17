from django.contrib.auth import authenticate
from audit.backend import ssh_interactive
from audit import models
# from django.conf import settings
# import subprocess
import getpass
import datetime
# import random
# import string


class UserShell(object):
    def __init__(self, sys_argv):
        self.sys_argv = sys_argv
    
    def auth(self):
        """
        auth function
        True: user object
        False: None
        """
        count = 0
        while count < 3:
            username = input("username:").strip()
            password = getpass.getpass("password:").strip()
            user = authenticate(username=username, password=password)
            if not user:
                count += 1
                print("Invalid username or password")
                continue
            self.user = user
            return True
        else:
            print("too many attempts!")
            return False

    def token_auth(self):
        count = 0
        while True: 
            token = input("Login Token:")
            if count == 3:
                exit
            if not token:
                return None
            if len(token) != 8:
                print('incorrect token!')
                count += 1
                continue
            
            expire_time = datetime.datetime.now() - datetime.timedelta(seconds=300)
            token_obj = models.LoginToken.objects.filter(
                val=token, date__gt=expire_time)
            if not token_obj:
                print('incorrect token!')
                count += 1
                continue
            self.user = token_obj.account.user
            return token_obj

    def start(self):
        token_obj = self.token_auth()
        if token_obj:
            selected_host = token_obj.host_user_bind
            ssh_interactive.connect(self.user, selected_host)
            exit

        if not self.auth():
            return None

        index_list = []
        while True:
            host_groups = self.user.account.host_groups.all()
            # groups list
            for i, v in enumerate(host_groups):
                print("%s\t%s[%s]" % (i, v, v.host_user_binds.count()))
                index_list.append(i)
            # UnGroup host
            print("%s\tUnGroup[%s]" % (
                len(host_groups), 
                self.user.account.host_user_binds.count()))
            # Choice host
            choice = input(">").strip()
            if choice.isdigit():
                choice = int(choice)
            host_bind = None
            if choice in index_list:
                host_bind = host_groups[choice].host_user_binds.all()
            if choice == len(host_groups):
                host_bind = self.user.account.host_user_binds.all()
            if not host_bind:
                print("None Host")
                continue
            index_list1 = []
            while True:
                # hostlist print
                for ii, vv in enumerate(host_bind):
                    print("%s\t%s" % (ii, vv))
                    index_list1.append(ii)
                choice1 = input("> UnGroup >")
                if choice1 == 'q':
                    break
                if choice1.isdigit():
                    choice1 = int(choice1)
                if choice1 not in index_list1:
                    continue
                selected_host = host_bind[choice1]
                print("selected host ", selected_host)
                ssh_interactive.connect(self.user, selected_host)
