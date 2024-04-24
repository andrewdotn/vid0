from django.shortcuts import redirect


def make_redirect_view(target):
    def handler(request):
        return redirect(target)

    return handler
