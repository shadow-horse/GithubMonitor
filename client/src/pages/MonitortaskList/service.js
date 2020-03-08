import request from '@/utils/request';
export async function queryRule(params) {
  return request('/server/monitor/task', {
    params,
  });
}
export async function removeRule(params) {
  console.log('removeRule', params);
  return request('/server/monitor/task', {
    method: 'POST',
    data: { ...params, method: 'remove' },
  });
}
export async function addRule(params) {
  return request('/server/monitor/task', {
    method: 'POST',
    data: { ...params, method: 'post' },
  });
}
export async function deleteRule(params) {
  console.log('deleteRule', params);
  return request('/server/monitor/task', {
    method: 'POST',
    data: { ...params, method:'delete'},
  });
}

export async function runscantask(params) {
  console.log('runscantask', params)
  return request('/server/scantask/runtask', {
    method: 'POST',
    data:{...params,method:'runtask'}
  });
}

export async function updateRule(params) {
  return request('/api/task', {
    method: 'POST',
    data: { ...params, method: 'update' },
  });
}
