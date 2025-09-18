// 全局变量
let websiteConfig = {};

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
  // 加载配置文件
  loadConfig();
  
  // 初始化页面
  initPage();
  
  // 移除加载动画
  setTimeout(function() {
    const loader = document.querySelector('.loader');
    if (loader) {
      loader.classList.add('fade-out');
    }
  }, 500);
});

// 加载JSON配置文件
function loadConfig() {
  fetch('/staic/KEY/json/website_config.json')
    .then(response => {
      if (!response.ok) {
        throw new Error('网络响应异常');
      }
      return response.json();
    })
    .then(data => {
      websiteConfig = data;
      updateWebsiteContent();
    })
    .catch(error => {
      console.error('加载配置文件失败:', error);
      // 使用默认配置
      useDefaultConfig();
    });
}

// 使用默认配置
function useDefaultConfig() {
  websiteConfig = {
    site: {
      title: "项目介绍网站",
      description: "一个现代化、美观且功能丰富的项目介绍网站",
      keywords: "项目介绍,现代化设计,精美UI,动画效果"
    },
    header: {
      logo_text: "CompearProject",
      nav_items: [
        {"title": "首页", "href": "#hero"},
        {"title": "关于我们", "href": "#about"},
        {"title": "项目功能", "href": "#features"},
        {"title": "技术栈", "href": "#technology"},
        {"title": "联系我们", "href": "#contact"}
      ]
    }
    // 其他默认配置...
  };
  updateWebsiteContent();
}

// 更新网站内容
function updateWebsiteContent() {
  // 更新网站元数据
  if (websiteConfig.site) {
    document.title = websiteConfig.site.title;
    
    const descriptionMeta = document.querySelector('meta[name="description"]');
    if (descriptionMeta && websiteConfig.site.description) {
      descriptionMeta.content = websiteConfig.site.description;
    }
    
    const keywordsMeta = document.querySelector('meta[name="keywords"]');
    if (keywordsMeta && websiteConfig.site.keywords) {
      keywordsMeta.content = websiteConfig.site.keywords;
    }
  }
  
  // 更新头部导航
  if (websiteConfig.header) {
    // 更新logo
    const logo = document.querySelector('.logo');
    if (logo && websiteConfig.header.logo_text) {
      logo.textContent = websiteConfig.header.logo_text;
    }
    
    // 更新导航菜单
    const navMenu = document.querySelector('.nav-menu');
    if (navMenu && websiteConfig.header.nav_items) {
      // 清空现有菜单
      navMenu.innerHTML = '';
      
      // 添加新菜单
      websiteConfig.header.nav_items.forEach(item => {
        const li = document.createElement('li');
        li.className = 'nav-item';
        
        const a = document.createElement('a');
        a.className = 'nav-link';
        a.href = item.href;
        a.textContent = item.title;
        
        li.appendChild(a);
        navMenu.appendChild(li);
      });
    }
  }
  
  // 更新英雄区域
  if (websiteConfig.hero) {
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle && websiteConfig.hero.title) {
      heroTitle.textContent = websiteConfig.hero.title;
    }
    
    const heroSubtitle = document.querySelector('.hero-subtitle');
    if (heroSubtitle && websiteConfig.hero.subtitle) {
      heroSubtitle.textContent = websiteConfig.hero.subtitle;
    }
    
    const ctaButton = document.querySelector('.cta-button');
    if (ctaButton) {
      if (websiteConfig.hero.cta_button) {
        ctaButton.textContent = websiteConfig.hero.cta_button;
      }
      if (websiteConfig.hero.cta_link) {
        ctaButton.href = websiteConfig.hero.cta_link;
      }
    }
  }
  
  // 更新其他区域内容...
}

// 初始化页面
function initPage() {
  // 导航菜单切换
  const menuToggle = document.querySelector('.menu-toggle');
  const navMenu = document.querySelector('.nav-menu');
  
  if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', function() {
      navMenu.classList.toggle('active');
      menuToggle.classList.toggle('active');
    });
  }
  
  // 滚动时改变导航栏样式
  const header = document.querySelector('.header');
  
  if (header) {
    window.addEventListener('scroll', function() {
      if (window.scrollY > 50) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    });
  }
  
  // 平滑滚动
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href');
      const targetElement = document.querySelector(targetId);
      
      if (targetElement) {
        // 关闭移动菜单
        if (navMenu && navMenu.classList.contains('active')) {
          navMenu.classList.remove('active');
          if (menuToggle) {
            menuToggle.classList.remove('active');
          }
        }
        
        // 平滑滚动到目标位置
        window.scrollTo({
          top: targetElement.offsetTop - 80, // 考虑导航栏高度
          behavior: 'smooth'
        });
      }
    });
  });
  
  // 添加元素进入视口时的动画效果
  const animatedElements = document.querySelectorAll('.feature-card, .tech-card, .about-image, .contact-form');
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, {
    threshold: 0.1
  });
  
  animatedElements.forEach(element => {
    element.style.opacity = '0';
    element.style.transform = 'translateY(20px)';
    element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(element);
  });
  
  // 表单提交处理
  const contactForm = document.querySelector('.contact-form');
  
  if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // 这里可以添加表单验证和提交逻辑
      alert('感谢您的留言！我们会尽快回复您。');
      contactForm.reset();
    });
  }
}

// 移动端菜单按钮动画
function toggleMenuAnimation() {
  const menuToggle = document.querySelector('.menu-toggle');
  
  if (menuToggle) {
    menuToggle.classList.toggle('active');
    
    const spans = menuToggle.querySelectorAll('span');
    
    if (menuToggle.classList.contains('active')) {
      spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
      spans[1].style.opacity = '0';
      spans[2].style.transform = 'rotate(-45deg) translate(7px, -7px)';
    } else {
      spans[0].style.transform = 'none';
      spans[1].style.opacity = '1';
      spans[2].style.transform = 'none';
    }
  }
}

// 添加到menuToggle的事件监听器
document.addEventListener('DOMContentLoaded', function() {
  const menuToggle = document.querySelector('.menu-toggle');
  
  if (menuToggle) {
    menuToggle.addEventListener('click', toggleMenuAnimation);
  }
});

// 响应式图片处理
function handleResponsiveImages() {
  const images = document.querySelectorAll('img[data-src]');
  
  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
        imageObserver.unobserve(img);
      }
    });
  });
  
  images.forEach(img => {
    imageObserver.observe(img);
  });
}

// 在页面加载完成后执行
window.addEventListener('load', function() {
  handleResponsiveImages();
  
  // 添加页面加载完成后的动画
  document.body.classList.add('loaded');
});

// 调整视口大小时重新处理响应式元素
window.addEventListener('resize', function() {
  handleResponsiveImages();
  
  // 确保在大屏幕上菜单是展开的
  const navMenu = document.querySelector('.nav-menu');
  const menuToggle = document.querySelector('.menu-toggle');
  
  if (window.innerWidth > 768) {
    if (navMenu && navMenu.classList.contains('active')) {
      navMenu.classList.remove('active');
      if (menuToggle) {
        menuToggle.classList.remove('active');
        toggleMenuAnimation(); // 重置菜单按钮样式
      }
    }
  }
});