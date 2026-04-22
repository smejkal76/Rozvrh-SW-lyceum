{% extends 'base.html' %}
{% block content %}
<h1>Editace učebny</h1>
<form method="post" action="/classrooms/{{ ucebna.id }}">
  <input name="nazev" value="{{ ucebna.nazev }}" required>
  <button type="submit">Uložit</button>
  <a href="/view/classrooms">Zrušit</a>
</form>
{% endblock %}