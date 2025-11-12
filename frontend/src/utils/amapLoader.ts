/**
 * 高德地图API加载器
 * 使用Vite的环境变量语法正确加载API密钥和安全密钥
 */

// 从环境变量获取配置（支持运行时和构建时）
const getEnvVar = (key: string): string => {
  // 优先使用运行时环境变量（适用于Docker生产环境）
  if (typeof window !== 'undefined' && window.env && window.env[key]) {
    return window.env[key];
  }
  // 回退到构建时环境变量（适用于开发环境）
  return import.meta.env[key] || '';
};

const API_KEY = getEnvVar('VITE_MAP_API_KEY');
const SECURITY_CODE = getEnvVar('VITE_MAP_SECURITY_CODE');

console.log('🔧 高德地图配置检查:');
console.log('- API密钥:', API_KEY ? '已配置' : '未配置');
console.log('- 安全密钥:', SECURITY_CODE ? '未配置' : '未配置');
console.log('- 环境变量来源:', typeof window !== 'undefined' && window.env ? '运行时' : '构建时');

// 全局加载状态
let isAMapLoaded = false;
let placeSearchPluginLoaded = false; // 修改变量名，避免与函数名冲突
let drivingPluginLoaded = false; // 新增：Driving插件加载状态
let loadPromise: Promise<void> | null = null;
let placeSearchPromise: Promise<void> | null = null;
let drivingPromise: Promise<void> | null = null; // 新增：Driving插件加载Promise

/**
 * 配置高德地图安全设置
 */
const configureSecurity = () => {
  if (SECURITY_CODE) {
    window._AMapSecurityConfig = {
      securityJsCode: SECURITY_CODE
    };
    console.log('✅ 安全配置已设置');
  } else {
    console.warn('⚠️ 安全密钥未配置，地图功能可能受限');
  }
};

/**
 * 加载高德地图API
 */
export const loadAMapAPI = (): Promise<void> => {
  if (isAMapLoaded) {
    console.log('✅ 高德地图API已加载');
    return Promise.resolve();
  }

  if (loadPromise) {
    return loadPromise;
  }

  loadPromise = new Promise((resolve, reject) => {
    // 检查配置
    if (!API_KEY) {
      const error = new Error('高德地图API密钥未配置');
      console.error('❌', error.message);
      reject(error);
      return;
    }

    // 配置安全设置
    configureSecurity();

    console.log('🚀 开始加载高德地图API...');

    // 检查是否已加载
    if (typeof window.AMap !== 'undefined') {
      console.log('✅ 高德地图API已存在');
      isAMapLoaded = true;
      resolve();
      return;
    }

    // 创建script标签加载API
    const script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${API_KEY}`;
    script.async = true;

    script.onload = () => {
      console.log('✅ 高德地图API加载成功');
      isAMapLoaded = true;
      
      // 检查AMap对象是否可用
      if (typeof window.AMap !== 'undefined') {
        console.log('✅ AMap对象已就绪');
        resolve();
      } else {
        const error = new Error('AMap对象未定义');
        console.error('❌', error.message);
        reject(error);
      }
    };

    script.onerror = (err) => {
      const error = new Error(`高德地图API加载失败: ${err}`);
      console.error('❌', error.message);
      reject(error);
    };

    document.head.appendChild(script);
  });

  return loadPromise;
};

/**
 * 加载高德地图API和所有必要插件
 */
export const loadAMapWithPlugins = (): Promise<void> => {
  if (isAMapAPILoaded() && isPlaceSearchPluginLoaded() && isDrivingPluginLoaded()) {
    console.log('✅ 高德地图API和所有插件已加载');
    return Promise.resolve();
  }

  console.log('🚀 开始加载高德地图API和所有插件...');

  return new Promise((resolve, reject) => {
    // 检查配置
    if (!API_KEY) {
      const error = new Error('高德地图API密钥未配置');
      console.error('❌', error.message);
      reject(error);
      return;
    }

    // 配置安全设置
    configureSecurity();

    // 检查是否已加载
    if (isAMapAPILoaded() && isPlaceSearchPluginLoaded() && isDrivingPluginLoaded()) {
      console.log('✅ 高德地图API和所有插件已存在');
      resolve();
      return;
    }

    // 创建script标签加载API和所有插件
    const script = document.createElement('script');
    script.type = 'text/javascript';
    // 一次性加载所有需要的插件
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${API_KEY}&plugin=AMap.PlaceSearch,AMap.Driving`;
    script.async = true;

    script.onload = () => {
      console.log('✅ 高德地图API和插件加载成功');
      
      // 等待所有组件完全初始化
      setTimeout(() => {
        // 检查核心API是否可用
        if (typeof window.AMap === 'undefined') {
          const error = new Error('AMap对象未定义');
          console.error('❌', error.message);
          reject(error);
          return;
        }

        // 标记为已加载
        isAMapLoaded = true;
        
        // 检查插件是否可用，但不强制要求
        if (typeof window.AMap.PlaceSearch !== 'undefined') {
          placeSearchPluginLoaded = true;
          console.log('✅ PlaceSearch插件已就绪');
        } else {
          console.warn('⚠️ PlaceSearch插件可能未完全加载');
        }
        
        if (typeof window.AMap.Driving !== 'undefined') {
          drivingPluginLoaded = true;
          console.log('✅ Driving插件已就绪');
        } else {
          console.warn('⚠️ Driving插件可能未完全加载');
        }

        console.log('✅ 高德地图初始化完成');
        resolve();
      }, 1000); // 给插件一些时间初始化
    };

    script.onerror = (err) => {
      const error = new Error(`高德地图API加载失败: ${err}`);
      console.error('❌', error.message);
      reject(error);
    };

    document.head.appendChild(script);
  });
};

/**
 * 加载高德地图PlaceSearch插件
 */
export const loadPlaceSearchPlugin = (): Promise<void> => {
  if (isPlaceSearchPluginLoaded()) {
    console.log('✅ PlaceSearch插件已加载');
    return Promise.resolve();
  }

  // 如果插件未加载，直接使用loadAMapWithPlugins来加载所有插件
  return loadAMapWithPlugins().then(() => {
    if (!isPlaceSearchPluginLoaded()) {
      throw new Error('PlaceSearch插件加载失败');
    }
  });
};

/**
 * 加载高德地图Driving插件（路径规划）
 */
export const loadDrivingPlugin = (): Promise<void> => {
  if (drivingPluginLoaded) {
    console.log('✅ Driving插件已加载');
    return Promise.resolve();
  }

  // 如果插件未加载，直接使用loadAMapWithPlugins来加载所有插件
  return loadAMapWithPlugins().then(() => {
    if (!isDrivingPluginLoaded()) {
      throw new Error('Driving插件加载失败');
    }
  });
};

/**
 * 检查Driving插件是否已加载
 */
export const isDrivingPluginLoaded = (): boolean => {
  return typeof window.AMap !== 'undefined' && 
         typeof window.AMap.Driving !== 'undefined';
};

/**
 * 等待Driving插件加载完成
 */
export const waitForDriving = (timeout = 30000): Promise<void> => {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const check = () => {
      if (isDrivingPluginLoaded()) {
        resolve();
      } else if (Date.now() - startTime > timeout) {
        reject(new Error('Driving插件加载超时'));
      } else {
        setTimeout(check, 500);
      }
    };
    
    check();
  });
};

/**
 * 检查高德地图API是否已加载
 */
export const isAMapAPILoaded = (): boolean => {
  return isAMapLoaded && typeof window.AMap !== 'undefined';
};

/**
 * 检查PlaceSearch插件是否已加载
 */
export const isPlaceSearchPluginLoaded = (): boolean => {
  // 直接检查全局变量和插件对象，不使用变量名
  return typeof window.AMap !== 'undefined' && 
         typeof window.AMap.PlaceSearch !== 'undefined';
};

/**
 * 等待高德地图API加载完成
 */
export const waitForAMap = (timeout = 30000): Promise<void> => {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const check = () => {
      if (isAMapAPILoaded()) {
        resolve();
      } else if (Date.now() - startTime > timeout) {
        reject(new Error('高德地图API加载超时'));
      } else {
        setTimeout(check, 500);
      }
    };
    
    check();
  });
};

/**
 * 等待PlaceSearch插件加载完成
 */
export const waitForPlaceSearch = (timeout = 30000): Promise<void> => {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();
    
    const check = () => {
      if (isPlaceSearchPluginLoaded()) {
        resolve();
      } else if (Date.now() - startTime > timeout) {
        reject(new Error('PlaceSearch插件加载超时'));
      } else {
        setTimeout(check, 500);
      }
    };
    
    check();
  });
};