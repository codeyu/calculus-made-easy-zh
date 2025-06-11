var ditto = {
    // page element ids
    content_id: "#content",
    sidebar_id: "#sidebar",
    edit_id: "#edit",
    back_to_top_id: "#back_to_top",
    loading_id: "#loading",
    error_id: "#error",

    // display elements
    sidebar: true,
    edit_button: true,
    back_to_top_button: true,
    save_progress: true, // 保存阅读进度
    search_bar: true,

    // initialize function
    run: initialize
};

/**
 * 获取当前hash
 *
 * @param {string} hash 要解析的hash，默认取当前页面的hash，如： nav#类目 => {nav:nav, anchor:类目}
 * @description 分导航和页面锚点
 * @return {Object} {nav:导航, anchor:页面锚点}
 */
var getHash = function (hash) {
  hash = hash || window.location.hash.substr(1);

  if (!hash) {
    return {
      nav: '',
      anchor: ''
    }
  }

  hash = hash.split('#');
  return {
    nav: hash[0],
    anchor: decodeURIComponent(hash[1] || '')
  }
};

var menu = new Array();

function initialize() {
  // initialize sidebar and buttons
  if (ditto.sidebar) {
    init_sidebar_section();
    init_sidebar_features();  // 添加新的侧边栏功能
  }

  if (ditto.back_to_top_button) {
    init_back_to_top_button();
  }

  if (ditto.edit_button) {
    init_edit_button();
  }

  // page router
  router();
  $(window).on('hashchange', router);
}

function init_sidebar_section() {
    $.get(ditto.sidebar_file, function (data) {
        $('#sidebar .sidebar-content').html(marked(data));

        if (ditto.search_bar) {
           init_searchbar();
        }

        // 初始化内容数组
        var menuOL = $('#sidebar .sidebar-content ol');
        menuOL.attr('start', 0);

        menuOL.find('li a').map(function() {
            menu.push(this.href.slice(this.href.indexOf('#')));
        });
        $('#pageup').on('click', function() {
            var hash = getHash().nav;
            for (var i = 0; i < menu.length; i++) {
                if (hash === '') break;
                if (menu[i] === '#' + hash) break;
            }
            location.hash = menu[i - 1]
        });
        $('#pagedown').on('click', function() {
            var hash = getHash().nav;
            for (var i = 0; i < menu.length; i++) {
                if (hash === '') break;
                if (menu[i] === '#' + hash) break;
            }
            location.hash = menu[i + 1];
        });
    }, "text").fail(function() {
        alert("Opps! can't find the sidebar file to display!");
    });
}

function init_searchbar() {
  var search = '<form class="searchBox" onSubmit="return searchbar_listener()">' +
    '<input name="search" type="search">' +
    '<input type="image" class="searchButton" src="images/magnifier.jpg" alt="Search" />' +
//    '<a class="searchLink" href="#" target="_blank"><img src="images/magnifier.jpg"></a>' +
    '</form>';
  $(ditto.sidebar_id).find('h2').first().before($(search));
  // $('input.searchButton').click(searchbar_listener);
  // $('input[name=search]').keydown(searchbar_listener);
}

function searchbar_listener(event) {
    // event.preventDefault();
    var q = $('input[name=search]').val();
    if (q !== '') {
      var url = 'https://github.com/codeyu/the-wisdom-of-trade-stocks/search?utf8=✓&q=' + encodeURIComponent(q);
      window.open(url, '_blank');
      win.focus();
    }
    return false;
  /*
  if (event.which === 13) {
    var q = $('input[name=search]').val();
    if (q !== '') {
      var url = 'https://github.com/ruanyf/es6tutorial/search?utf8=✓&q=' + encodeURIComponent(q);
      location.href = url;
    }
  }
  */
}


function init_back_to_top_button() {
  // 只在非移动端显示
  if (window.innerWidth >= 640) {  // 40rem = 640px
    $(ditto.back_to_top_id).show();
    $(ditto.back_to_top_id).on('click', goTop);
  }
}

function goTop(e) {
  if(e) e.preventDefault();
  $('html, body').animate({
    scrollTop: 0
  }, 200);
  history.pushState(null, null, '#' + location.hash.split('#')[1]);
}

function goSection(sectionId){
  $('html, body').animate({
    scrollTop: ($('#' + sectionId).offset().top)
  }, 300);
}

function init_edit_button() {
  if (ditto.base_url === null) {
    alert("Error! You didn't set 'base_url' when calling ditto.run()!");
  } else {
    // 只在非移动端显示
    if (window.innerWidth >= 640) {  // 40rem = 640px
      $(ditto.edit_id).show();
      $(ditto.edit_id).on("click", function() {
        var hash = location.hash.replace("#", "/");
        if (/#.*$/.test(hash)) {
          hash = hash.replace(/#.*$/, '');
        }
        if (hash === "") {
          hash = "/" + ditto.index.replace(".md", "");
        }

        window.open(ditto.base_url + hash + ".md");
      });
    }
  }
}

function replace_symbols(text) {
  // replace symbols with underscore
  return text
    .replace(/, /g, ',')
    .replace(/[&\/\\#,.+=$~%'":*?<>{}\ \]\[]/g, "-")
    .replace(/[()]/g, '');
}

function li_create_linkage(li_tag, header_level) {
  // add custom id and class attributes
  html_safe_tag = replace_symbols(li_tag.text());
  li_tag.attr('data-src', html_safe_tag);
  li_tag.attr("class", "link");

  // add click listener - on click scroll to relevant header section
  li_tag.click(function(e) {
    e.preventDefault();
    // scroll to relevant section
    var header = $(
      ditto.content_id + " h" + header_level + "." + li_tag.attr('data-src')
    );
    $('html, body').animate({
      scrollTop: header.offset().top
    }, 200);

    // highlight the relevant section
    original_color = header.css("color");
    header.animate({ color: "#ED1C24", }, 500, function() {
      // revert back to orig color
      $(this).animate({color: original_color}, 2500);
    });
    history.pushState(null, null, '#' + location.hash.split('#')[1] + '#' + li_tag.attr('data-src'));
  });
}

function create_page_anchors() {
  // create page anchors by matching li's to headers
  // if there is a match, create click listeners
  // and scroll to relevant sections

  // go through header level 1 to 3
  for (var i = 2; i <= 4; i++) {
    // parse all headers
    var headers = [];
    $('#content h' + i).map(function() {
      var content = $(this).text();
      headers.push(content);
      $(this).addClass(replace_symbols(content));
      this.id = replace_symbols(content);
      
      // 存储原始HTML，包括已渲染的数学公式
      var originalHtml = $(this).html();
      
      $(this).hover(function () {
        // 在原始HTML后添加链接，而不是替换整个内容
        $(this).html(originalHtml +
          ' <a href="#' + location.hash.split('#')[1] +
          '#' +
          replace_symbols(content) +
          '" class="section-link">§</a> <a href="#' +
          location.hash.split('#')[1] + '" onclick="goTop()">⇧</a>');
      }, function () {
        // 恢复原始HTML，保持数学公式的渲染状态
        $(this).html(originalHtml);
      });

      // 确保hover事件不会破坏数学公式渲染
      $(this).on('mouseenter mouseleave', function() {
        renderMathInElement(this, {
          delimiters: [
              {left: '$$', right: '$$', display: true},
              {left: '$', right: '$', display: false},
              {left: '\\(', right: '\\)', display: false},
              {left: '\\[', right: '\\]', display: true}
          ],
          throwOnError: false,
          output: 'html',
          strict: false
        });
      });
      
      $(this).on('click', 'a.section-link', function(event) {
        event.preventDefault();
        history.pushState(null, null, '#' + location.hash.split('#')[1] + '#' + replace_symbols(content));
        goSection(replace_symbols(content));
      });
    });

    if ((i === 2) && headers.length !== 0) {
      var ul_tag = $('<ol></ol>')
        .insertAfter('#content h1')
        .addClass('content-toc')
        .attr('id', 'content-toc');
      for (var j = 0; j < headers.length; j++) {
        var li_tag = $('<li></li>').html('<a href="#' + location.hash.split('#')[1] + '#' + headers[j] + '">' + headers[j] + '</a>');
        ul_tag.append(li_tag);
        li_create_linkage(li_tag, i);
      }
    }
  }
}

function normalize_paths() {
  // images
  $(ditto.content_id + " img").map(function() {
    var src = $(this).attr("src");
    if($(this).attr("src").indexOf("../") > -1){
      src = $(this).attr("src").replace("../", "");
      $(this).attr("src", "http://" + location.host + "/" + src);
    }
    else{
      src = $(this).attr("src").replace("./", "");
      if ($(this).attr("src").slice(0, 4) !== "http") {
        var pathname = location.pathname.substr(0, location.pathname.length - 1);
        var url = location.hash.replace("#", "");

        // split and extract base dir
        url = url.split("/");
        var base_dir = url.slice(0, url.length - 1).toString();

        // normalize the path (i.e. make it absolute)
        $(this).attr("src", pathname + base_dir + "/" + src);
      }
    }
  });
}

function show_error() {
  console.log("SHOW ERORR!");
  $(ditto.error_id).show();
}

function show_loading() {
  $(ditto.loading_id).show();
  $(ditto.content_id).html('');  // clear content

  // infinite loop until clearInterval() is called on loading
  var loading = setInterval(function() {
    $(ditto.loading_id).fadeIn(1000).fadeOut(1000);
  }, 2000);

  return loading;
}

function router() { 
  var path = location.hash.replace(/#([^#]*)(#.*)?/, './$1');

  var hashArr = location.hash.split('#');
  var sectionId;
  if (hashArr.length > 2 && !(/^comment-/.test(hashArr[2]))) {
    sectionId = hashArr[2];
  }

  if (ditto.save_progress && store.get('menu-progress') !== location.hash) {
    store.set('menu-progress', location.hash);
    store.set('page-progress', 0);
  }

  // default page if hash is empty
  if (location.pathname === "/index.html") {
    path = location.pathname.replace("index.html", ditto.index);
    normalize_paths();
  } else if (path === "") {
    path = location.pathname + ditto.index;
    normalize_paths();
  } else {
    path = path + ".md";
  }

  // 取消scroll事件的监听函数
  // 防止改变下面的变量perc的值
  $(window).off('scroll');

  // otherwise get the markdown and render it
  var loading = show_loading();
  $.get(path, function(data) {
    $(ditto.error_id).hide();
    $(ditto.content_id).html(marked(data));
    if ($(ditto.content_id + " h1").text() === ditto.document_title) {
      document.title = ditto.document_title;
    } else {
      document.title = $(ditto.content_id + " h1").text() + " - " + ditto.document_title;
    }
    normalize_paths();
    create_page_anchors();

    // 完成代码高亮
    $('#content code').map(function() {
      Prism.highlightElement(this);
    });

    // 渲染数学公式 - 添加小延时确保在其他DOM操作后执行
    setTimeout(function() {
      renderMathInElement(document.getElementById('content'), {
          delimiters: [
              {left: '$$', right: '$$', display: true},
              {left: '$', right: '$', display: false},
              {left: '\\(', right: '\\)', display: false},
              {left: '\\[', right: '\\]', display: true}
          ],
          throwOnError: false,
          output: 'html',  // 使用html输出以避免与其他渲染冲突
          strict: false,    // 放宽严格模式以提高兼容性
          trust: true,
          macros: {},
          minRuleThickness: 0.05,
          maxSize: Infinity,
          maxExpand: 1000,
          globalGroup: true,  // 启用全局分组以避免样式冲突
          displayMode: false  // 默认使用行内模式，让 delimiters 控制显示模式
      });
    }, 100);

    var perc = ditto.save_progress ? store.get('page-progress') || 0 : 0;

    if (sectionId) {
      $('html, body').animate({
        scrollTop: ($('#' + decodeURI(sectionId)).offset().top)
      }, 300);
    } else {
      if (location.hash !== '' || Boolean(perc)) {
        if (!Boolean(perc)) {
          $('html, body').animate({
            scrollTop: ($('#content').offset().top + 10)
          }, 300);
          $('html, body').animate({
            scrollTop: ($('#content').offset().top)
          }, 300);
        } else {
          $('html, body').animate({
            scrollTop: ($('body').height()-$(window).height())*perc
          }, 200);
        }
      }
    }
    if (location.hash === '' || '#' + getHash().nav === menu[0]) {
      $('#pageup').css('display', 'none');
    } else {
      $('#pageup').css('display', 'inline-block');
    }

    if ('#' + getHash().nav === menu[(menu.length - 1)]) {
      $('#pagedown').css('display', 'none');
    } else {
      $('#pagedown').css('display', 'inline-block');
    }

    (function() {
      var $w = $(window);
      var $prog2 = $('.progress-indicator-2');
      var wh = $w.height();
      var h = $('body').height();
      var sHeight = h - wh;
      $w.on('scroll', function() {
        window.requestAnimationFrame(function(){
          var perc = Math.max(0, Math.min(1, $w.scrollTop() / sHeight));
          updateProgress(perc);
        });
      });

      function updateProgress(perc) {
        $prog2.css({width: perc * 100 + '%'});
        ditto.save_progress && store.set('page-progress', perc);
      }

    }());

  }).fail(function() {
    show_error();
  }).always(function() {
    clearInterval(loading);
    $(ditto.loading_id).hide();
  });
}

// 添加窗口大小变化的监听
$(window).on('resize', function() {
  if (window.innerWidth >= 640) {
    if (ditto.back_to_top_button) {
      $(ditto.back_to_top_id).show();
    }
    if (ditto.edit_button) {
      $(ditto.edit_id).show();
    }
  } else {
    $(ditto.back_to_top_id).hide();
    $(ditto.edit_id).hide();
  }
});

// 添加新的侧边栏功能初始化函数
function init_sidebar_features() {
    // 侧边栏切换功能
    $('#sidebar-toggle').on('click', function() {
        var $sidebar = $('#sidebar');
        var $overlay = $('#sidebar-overlay');
        var isMobile = window.innerWidth < 640;

        if (isMobile) {
            // 移动端逻辑
            if ($sidebar.hasClass('visible')) {
                $sidebar.removeClass('visible');
                $overlay.removeClass('visible');
                setTimeout(function() {
                    $overlay.hide();
                }, 300); // 等待过渡动画完成
            } else {
                $overlay.show();
                setTimeout(function() {
                    $sidebar.addClass('visible');
                    $overlay.addClass('visible');
                }, 10); // 确保显示后再添加过渡效果
            }
        } else {
            // 桌面端逻辑
            $('#sidebar').toggleClass('hidden');
            $('#content').toggleClass('sidebar-hidden');
            
            // 更新翻页按钮位置
            if ($('#content').hasClass('sidebar-hidden')) {
                $('#flip').css('left', '50%');
            } else {
                if (window.innerWidth >= 640) {
                    $('#flip').css('left', 'calc(50% + 165px)');
                }
            }
            
            // 保存状态到 localStorage
            var isHidden = $('#sidebar').hasClass('hidden');
            localStorage.setItem('sidebar-hidden', isHidden);
        }
    });

    // 点击遮罩层关闭侧边栏
    $('#sidebar-overlay').on('click', function() {
        $('#sidebar').removeClass('visible');
        $(this).removeClass('visible');
        setTimeout(function() {
            $('#sidebar-overlay').hide();
        }, 300);
    });

    // 从 localStorage 恢复状态（仅桌面端）
    if (window.innerWidth >= 640 && localStorage.getItem('sidebar-hidden') === 'true') {
        $('#sidebar').addClass('hidden');
        $('#content').addClass('sidebar-hidden');
        $('#flip').css('left', '50%');
    }

    // 侧边栏宽度调整功能
    var $sidebar = $('#sidebar');
    var $resizer = $('#sidebar-resizer');
    var $content = $('#content');
    var isResizing = false;
    var lastDownX = 0;
    var originalWidth = parseInt(localStorage.getItem('sidebar-width')) || 280;
    
    // 恢复保存的宽度
    if (originalWidth !== 280) {
        $sidebar.width(originalWidth);
        $resizer.css('left', originalWidth + 'px');
        $content.css('padding-left', (originalWidth + 70) + 'px');
    }

    $resizer.on('mousedown', function(e) {
        isResizing = true;
        lastDownX = e.clientX;
        e.preventDefault();
    });

    $(document).on('mousemove', function(e) {
        if (!isResizing) return;

        var newWidth = originalWidth + (e.clientX - lastDownX);
        if (newWidth < 150) newWidth = 150;  // 最小宽度
        if (newWidth > 600) newWidth = 600;  // 最大宽度

        $sidebar.width(newWidth);
        $resizer.css('left', newWidth + 'px');
        $content.css('padding-left', (newWidth + 70) + 'px');

        // 更新翻页按钮位置
        if (window.innerWidth >= 640) {  // 40rem = 640px
            var offset = Math.floor((newWidth - 280) / 2);  // 计算偏移量
            $('#flip').css('left', 'calc(50% + ' + (165 + offset) + 'px)');
        }
    });

    $(document).on('mouseup', function(e) {
        if (!isResizing) return;
        
        isResizing = false;
        originalWidth = $sidebar.width();
        
        // 保存宽度到 localStorage
        localStorage.setItem('sidebar-width', originalWidth);

        // 保存最终的翻页按钮位置
        if (window.innerWidth >= 640) {  // 40rem = 640px
            var offset = Math.floor((originalWidth - 280) / 2);  // 计算偏移量
            $('#flip').css('left', 'calc(50% + ' + (165 + offset) + 'px)');
        }
    });
}
