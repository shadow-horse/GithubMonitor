import request from '@/utils/request';


//获取task任务列表
export async function gettasklist(params) {
  return request('/api/scanlist', {
    method: 'POST',
    data: { ...params, method: 'gettasklist' },
  });
}

//根据task id获取扫描结果列表
export  function getscanlist(id) {
  return request('/api/scanlist', {
    method: 'POST',
    data: { id: { id }, method: 'getscanlist' },
  });
}
