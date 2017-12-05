/*jslint browser: true*/
/*global $*/


$(document).ready(function () {
  $('#serverside_table').DataTable({
    bProcessing: true,
    bServerSide: true,
    sPaginationType: "full_numbers",
    lengthMenu: [[20, 25, 50, 100], [20, 25, 50, 100]],
    order: [[2, "desc"]],
    iDisplayLength: 20,
    bjQueryUI: true,
    sAjaxSource: '/tables/serverside_table',
    columns: [
      {"data": "pmid"},
      {"data": "title"},
      {"data": "year"},
      {"data": "authors"}
    ]
  });
});
