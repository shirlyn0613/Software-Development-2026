"""City tree used by the Streamlit dashboard.

China is organized by provincial-level region and expanded to common
prefecture-level city / prefecture entries. United States and United Kingdom
do not use the Chinese "prefecture-level city" administrative concept, so they
are grouped by state / country-region with representative monitorable cities.
"""

CITY_TREE = {
    "China": {
        "Beijing": ["Beijing"],
        "Tianjin": ["Tianjin"],
        "Shanghai": ["Shanghai"],
        "Chongqing": ["Chongqing"],
        "Hebei": [
            "Shijiazhuang", "Tangshan", "Qinhuangdao", "Handan", "Xingtai",
            "Baoding", "Zhangjiakou", "Chengde", "Cangzhou", "Langfang",
            "Hengshui",
        ],
        "Shanxi": [
            "Taiyuan", "Datong", "Yangquan", "Changzhi", "Jincheng",
            "Shuozhou", "Jinzhong", "Yuncheng", "Xinzhou", "Linfen", "Lvliang",
        ],
        "Inner Mongolia": [
            "Hohhot", "Baotou", "Wuhai", "Chifeng", "Tongliao", "Ordos",
            "Hulunbuir", "Bayannur", "Ulanqab", "Hinggan", "Xilingol", "Alxa",
        ],
        "Liaoning": [
            "Shenyang", "Dalian", "Anshan", "Fushun", "Benxi", "Dandong",
            "Jinzhou", "Yingkou", "Fuxin", "Liaoyang", "Panjin", "Tieling",
            "Chaoyang", "Huludao",
        ],
        "Jilin": [
            "Changchun", "Jilin", "Siping", "Liaoyuan", "Tonghua", "Baishan",
            "Songyuan", "Baicheng", "Yanbian",
        ],
        "Heilongjiang": [
            "Harbin", "Qiqihar", "Jixi", "Hegang", "Shuangyashan", "Daqing",
            "Yichun", "Jiamusi", "Qitaihe", "Mudanjiang", "Heihe", "Suihua",
            "Daxing'anling",
        ],
        "Jiangsu": [
            "Nanjing", "Wuxi", "Xuzhou", "Changzhou", "Suzhou", "Nantong",
            "Lianyungang", "Huai'an", "Yancheng", "Yangzhou", "Zhenjiang",
            "Taizhou", "Suqian",
        ],
        "Zhejiang": [
            "Hangzhou", "Ningbo", "Wenzhou", "Jiaxing", "Huzhou", "Shaoxing",
            "Jinhua", "Quzhou", "Zhoushan", "Taizhou", "Lishui",
        ],
        "Anhui": [
            "Hefei", "Wuhu", "Bengbu", "Huainan", "Ma'anshan", "Huaibei",
            "Tongling", "Anqing", "Huangshan", "Chuzhou", "Fuyang", "Suzhou",
            "Lu'an", "Bozhou", "Chizhou", "Xuancheng",
        ],
        "Fujian": [
            "Fuzhou", "Xiamen", "Putian", "Sanming", "Quanzhou", "Zhangzhou",
            "Nanping", "Longyan", "Ningde",
        ],
        "Jiangxi": [
            "Nanchang", "Jingdezhen", "Pingxiang", "Jiujiang", "Xinyu",
            "Yingtan", "Ganzhou", "Ji'an", "Yichun", "Fuzhou", "Shangrao",
        ],
        "Shandong": [
            "Jinan", "Qingdao", "Zibo", "Zaozhuang", "Dongying", "Yantai",
            "Weifang", "Jining", "Tai'an", "Weihai", "Rizhao", "Linyi",
            "Dezhou", "Liaocheng", "Binzhou", "Heze",
        ],
        "Henan": [
            "Zhengzhou", "Kaifeng", "Luoyang", "Pingdingshan", "Anyang",
            "Hebi", "Xinxiang", "Jiaozuo", "Puyang", "Xuchang", "Luohe",
            "Sanmenxia", "Nanyang", "Shangqiu", "Xinyang", "Zhoukou",
            "Zhumadian", "Jiyuan",
        ],
        "Hubei": [
            "Wuhan", "Huangshi", "Shiyan", "Yichang", "Xiangyang", "Ezhou",
            "Jingmen", "Xiaogan", "Jingzhou", "Huanggang", "Xianning",
            "Suizhou", "Enshi", "Xiantao", "Qianjiang", "Tianmen", "Shennongjia",
        ],
        "Hunan": [
            "Changsha", "Zhuzhou", "Xiangtan", "Hengyang", "Shaoyang", "Yueyang",
            "Changde", "Zhangjiajie", "Yiyang", "Chenzhou", "Yongzhou",
            "Huaihua", "Loudi", "Xiangxi",
        ],
        "Guangdong": [
            "Guangzhou", "Shaoguan", "Shenzhen", "Zhuhai", "Shantou", "Foshan",
            "Jiangmen", "Zhanjiang", "Maoming", "Zhaoqing", "Huizhou", "Meizhou",
            "Shanwei", "Heyuan", "Yangjiang", "Qingyuan", "Dongguan", "Zhongshan",
            "Chaozhou", "Jieyang", "Yunfu",
        ],
        "Guangxi": [
            "Nanning", "Liuzhou", "Guilin", "Wuzhou", "Beihai", "Fangchenggang",
            "Qinzhou", "Guigang", "Yulin", "Baise", "Hezhou", "Hechi",
            "Laibin", "Chongzuo",
        ],
        "Hainan": ["Haikou", "Sanya", "Sansha", "Danzhou"],
        "Sichuan": [
            "Chengdu", "Zigong", "Panzhihua", "Luzhou", "Deyang", "Mianyang",
            "Guangyuan", "Suining", "Neijiang", "Leshan", "Nanchong", "Meishan",
            "Yibin", "Guang'an", "Dazhou", "Ya'an", "Bazhong", "Ziyang",
            "Aba", "Ganzi", "Liangshan",
        ],
        "Guizhou": [
            "Guiyang", "Liupanshui", "Zunyi", "Anshun", "Bijie", "Tongren",
            "Qianxinan", "Qiandongnan", "Qiannan",
        ],
        "Yunnan": [
            "Kunming", "Qujing", "Yuxi", "Baoshan", "Zhaotong", "Lijiang",
            "Pu'er", "Lincang", "Chuxiong", "Honghe", "Wenshan", "Xishuangbanna",
            "Dali", "Dehong", "Nujiang", "Diqing",
        ],
        "Tibet": [
            "Lhasa", "Shigatse", "Qamdo", "Nyingchi", "Shannan", "Nagqu", "Ngari",
        ],
        "Shaanxi": [
            "Xi'an", "Tongchuan", "Baoji", "Xianyang", "Weinan", "Yan'an",
            "Hanzhong", "Yulin", "Ankang", "Shangluo",
        ],
        "Gansu": [
            "Lanzhou", "Jiayuguan", "Jinchang", "Baiyin", "Tianshui", "Wuwei",
            "Zhangye", "Pingliang", "Jiuquan", "Qingyang", "Dingxi", "Longnan",
            "Linxia", "Gannan",
        ],
        "Qinghai": [
            "Xining", "Haidong", "Haibei", "Huangnan", "Hainan", "Golog",
            "Yushu", "Haixi",
        ],
        "Ningxia": ["Yinchuan", "Shizuishan", "Wuzhong", "Guyuan", "Zhongwei"],
        "Xinjiang": [
            "Urumqi", "Karamay", "Turpan", "Hami", "Changji", "Bortala",
            "Bayingolin", "Aksu", "Kizilsu", "Kashgar", "Hotan", "Ili",
            "Tacheng", "Altay", "Shihezi", "Alar", "Tumxuk", "Wujiaqu", "Beitun",
            "Tiemenguan", "Shuanghe", "Kokdala", "Kunyu", "Huyanghe",
        ],
        "Hong Kong": ["Hong Kong"],
        "Macau": ["Macau"],
        "Taiwan": [
            "Taipei", "New Taipei", "Taoyuan", "Taichung", "Tainan", "Kaohsiung",
            "Keelung", "Hsinchu", "Chiayi", "Yilan", "Hualien", "Taitung",
            "Penghu", "Kinmen", "Lienchiang",
        ],
    },
    "United States": {
        "California": ["Los Angeles", "San Francisco", "San Diego", "San Jose", "Sacramento", "Fresno"],
        "New York": ["New York", "Buffalo", "Rochester", "Syracuse", "Albany"],
        "Texas": ["Houston", "Dallas", "Austin", "San Antonio", "Fort Worth", "El Paso"],
        "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville", "Tallahassee"],
        "Illinois": ["Chicago", "Springfield", "Peoria", "Rockford"],
        "Washington": ["Seattle", "Tacoma", "Spokane", "Olympia"],
    },
    "United Kingdom": {
        "England": ["London", "Manchester", "Birmingham", "Liverpool", "Leeds", "Bristol", "Sheffield", "Newcastle"],
        "Scotland": ["Edinburgh", "Glasgow", "Aberdeen", "Dundee", "Inverness"],
        "Wales": ["Cardiff", "Swansea", "Newport", "Wrexham"],
        "Northern Ireland": ["Belfast", "Derry", "Lisburn", "Newry"],
    },
}
