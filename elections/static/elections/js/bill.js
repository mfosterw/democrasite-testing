function update_progress(_, pbar){
  let votes = $(pbar).siblings('.vote')
  let yes_votes = parseInt(votes.children('.num-yes-votes').text())
  let no_votes = parseInt(votes.children('.num-no-votes').text())
  $(pbar).children('.bg-success')
    .css('width', ((100 * yes_votes / (yes_votes + no_votes)) || 0) + '%')
  $(pbar).children('.bg-danger')
    .css('width', ((100 * no_votes / (yes_votes + no_votes)) || 0) + '%')
}

$(document).ready(function(){
  $('.progress').each(update_progress)
  $('[data-toggle="tooltip"]').tooltip()
})
