window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

function deleteVenue(id) {
  fetch(`/venues/${id}`, {
    method: 'DELETE',
  })
    .then((res) => {
      console.log(res);
      document.getElementById(id).remove();
    })
    .catch((err) => {
      console.log(err);
    });
}
