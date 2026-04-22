{% extends 'base.html' %}
{% block content %}
<h1>Učebny</h1>

{% for category, msg in get_flashed_messages(with_categories=True) %}
  <div class="alert {{ category }}">{{ msg }}</div>
{% endfor %}

<table>
  <tr><th>Název</th><th>Akce</th></tr>
  {% for u in ucebny %}
  <tr>
    <td>{{ u.nazev }}</td>
    <td>
      <a href="/view/classrooms/{{ u.id }}/edit">Editovat</a>
      <form method="post" action="/classrooms/{{ u.id }}/delete" style="display:inline">
        <button onclick="return confirm('Smazat {{ u.nazev }}?')">Smazat</button>
      </form>
    </td>
  </tr>
  {% endfor %}
</table>

<h2>Přidat učebnu</h2>
<form method="post" action="/classrooms">
  <input name="nazev" placeholder="Název učebny" required>
  <button type="submit">Přidat</button>
</form>

<a href="/view/day">← Zpět na rozvrh</a>
{% endblock %}