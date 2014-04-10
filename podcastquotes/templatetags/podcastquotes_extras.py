from django import template
register = template.Library()

@register.filter(name='addcss')
def addcss(field, css, placeholder):
    return field.as_widget(attrs={"class":css})