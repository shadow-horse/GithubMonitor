import { parse } from 'url';

// 扫描任务列表
const genList = (current, pageSize) => {
  const tableListDataSource = [];

  for (let i = 0; i < pageSize; i += 1) {
    const index = (current - 1) * 10 + i;
    tableListDataSource.push({
      key: index,
      name: `扫描任务 ${index}`,
      f_keys: 'www.vivo.com.cn',
      s_keys: 'password',
      repo_keys: 'username && password',
      parent_id: '10001',
      states: Math.floor(Math.random() * 10) % 4,
    });
  }

  tableListDataSource.reverse();
  return tableListDataSource;
};

let tableListDataSource = genList(1, 10);

//扫描结果列表

const genScanList = (current, pageSize) => {

  const listData = [];
  for (let i = 1; i <= current; i++) {
    listData.push({
      disable:false,
      id: `id=>${i}`,
      name: `index.html `,
      path: `hire/james-woodard/index.html => ${i} => ${current}`,
      sha: "2b8d66c525c9a2420f3dfe6dab1ea9967b92abc0",
      html_url: 'https://github.com/AustinCodingAcademy/preview.lubbockcodingacademy.com/blob/a68cba91912c68992070c86d687c2daf171b242d/hire/james-woodard/index.html',
      reponame: 'AustinCodingAcademy/preview.lubbockcodingacademy.com',
      avatar: '/github.jpg',
      keywords:
        'username',
      content: "",
    });
  }
  return listData;
}

let tableScanList = genScanList(5, 10);

function getRule(req, res, u) {
  let url = u;

  if (!url || Object.prototype.toString.call(url) !== '[object String]') {
    // eslint-disable-next-line prefer-destructuring
    url = req.url;
  }

  const { current = 1, pageSize = 10 } = req.query;
  const params = parse(url, true).query;
  let dataSource = [...tableListDataSource].slice((current - 1) * pageSize, current * pageSize);

  if (params.sorter) {
    const s = params.sorter.split('_');
    dataSource = dataSource.sort((prev, next) => {
      if (s[1] === 'descend') {
        return next[s[0]] - prev[s[0]];
      }

      return prev[s[0]] - next[s[0]];
    });
  }

  if (params.status) {
    const status = params.status.split(',');
    let filterDataSource = [];
    status.forEach(s => {
      filterDataSource = filterDataSource.concat(
        dataSource.filter(item => {
          if (parseInt(`${item.status}`, 10) === parseInt(s.split('')[0], 10)) {
            return true;
          }

          return false;
        }),
      );
    });
    dataSource = filterDataSource;
  }

  if (params.name) {
    dataSource = dataSource.filter(data => data.name.includes(params.name || ''));
  }

  const result = {
    data: dataSource,
    total: tableListDataSource.length,
    success: true,
    pageSize,
    current: parseInt(`${params.currentPage}`, 10) || 1,
  };
  return res.json(result);
}

function postRule(req, res, u, b) {
  let url = u;

  if (!url || Object.prototype.toString.call(url) !== '[object String]') {
    // eslint-disable-next-line prefer-destructuring
    url = req.url;
  }

  const body = (b && b.body) || req.body;
  const { method, id,key, name, f_keys, s_keys, repo_keys, parent_id, states } = body;

  switch (method) {
    //新增获取taskscanlist接口数据
    case 'gettasklist':
      return res.json(tableListDataSource);
      break;

    //根据任务id，获取对应的扫描结果
    case 'getscanlist':
      tableScanList = genScanList(id['id'], 10);
      return res.json(tableScanList);
      break;  

    default:
      break;
  }

  const result = {
    list: tableListDataSource,
    pagination: {
      total: tableListDataSource.length,
    },
  };
  res.json(result);
}

export default {
  'GET /api/scanlist': getRule,
  'POST /api/scanlist': postRule,
};
