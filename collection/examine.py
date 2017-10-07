#!/usr/bin/env python3
import collect


def is_username_in_use(name):
    return False


def validate_username(name):
    return name.isalpha() and name.islower() and 3 <= len(name) <= 12


def login():
    print("Remind me: What username did you provide? ")
    if validate_username(name):
        return name


def create_user():
    print("\nTo use the tool, you'll need to provide a username.")
    print("Your username must solely consist of lowercase letters, and must be between three and twelve characters long.")
    name = input("What would you like your username to be? ")
    
    if validate_username(name):
        if is_username_in_use(name):
            print("Well, this is awkward. It seems that the username you provided is already being used.")
            print("Let's try again...\n")
            return create_user()
        return name
    else:
        print("\nHmmm. You seem to have provided an invalid username.")
        print("Let's try this again...\n")
        return create_user()


def get_username():
    ans = input("Have you already used the tool? (y/n) ")

    if ans in ['n', 'no']:
        return create_user()

    elif ans in ['y', 'yes']:
        print("Excellent!")
        print("Sorry, I didn't recognise you; my creator is a rather sub-par programmer, to be frank.\n")
        return login()

    else:
        print("Hmmm. I didn't understand your input. Let's try that again...\n")
        return get_username()


if __name__ == '__main__':
    print("Hey! Thanks for helping us to annotate the ArduBugs dataset.")
    print("")

    username = get_username()

    print("\nWelcome back, {}".format(username))
