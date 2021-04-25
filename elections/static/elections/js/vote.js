$(document).ready(function(){
  const csrftoken = Cookies.get('csrftoken')
  $('.vote').click(function(){
    $.ajax($(this).attr('action'), {
      method: 'POST',
      headers: {'X-CSRFToken': csrftoken},
      data: {vote: $(this).attr('value')},
      context: $(this)
    }).done(function(data){
      this.toggleClass('font-weight-bold')
      this.siblings('.vote').removeClass('font-weight-bold')
      num = this.attr('id').split('-').slice(-1)[0]
      $('#num-yes-votes-' + num).text(data['yes-votes'])
      $('#num-no-votes-' + num).text(data['no-votes'])
      update_progress(0, this.siblings('.progress'))
    })
  })
})
