async function search() {
  const query = document.getElementById('query').value;
  if (!query.trim()) return;

  const searchBtn = document.getElementById('searchBtn');
  const resultsDiv = document.getElementById('results');
  resultsDiv.innerHTML = '<p>搜索中...</p>';
  searchBtn.disabled = true;

  try {
    const k = parseInt(document.getElementById('k').value) || 5;
    const resp = await fetch('/v1/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, k })
    });
    const data = await resp.json();
    const results = data.results;

    if (!results || results.length === 0) {
      resultsDiv.innerHTML = '<p>未找到结果。</p>';
      return;
    }

    let html = '';
    results.forEach(r => {
      const source = escapeHtml(r.source || '');
      const text = escapeHtml(r.text || '');
      const mime = escapeHtml(r.mime || '');
      html += `<div class="result-card">
        <div class="meta">
          <span class="source">${source}</span>
          <span>offset: ${r.offset}</span>
          <span class="score">相似度: ${(r.score * 100).toFixed(1)}%</span>
          <span>${mime}</span>
        </div>
        <p>${text.substring(0, 300)}${text.length > 300 ? '...' : ''}</p>`;
      
      if (r.extract_type === 'binary' && r.hex_preview) {
        html += `<div class="hex-preview">
          <strong>Hex Preview (前${r.hex_preview.length/2} 字节):</strong>
          <pre>${formatHex(r.hex_preview)}</pre>
        </div>`;
      }
      html += `</div>`;
    });
    resultsDiv.innerHTML = html;
  } catch (err) {
    resultsDiv.innerHTML = `<p style="color:red">错误: ${escapeHtml(err.message)}</p>`;
  } finally {
    searchBtn.disabled = false;
  }
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

function formatHex(hexStr) {
  let result = '';
  const bytes = hexStr.match(/.{1,32}/g); // group by 16 bytes = 32 hex chars
  if (!bytes) return hexStr;

  for (let i = 0; i < bytes.length; i++) {
    const hexLine = bytes[i].match(/.{1,2}/g).join(' ');
    let ascii = '';
    for (let j = 0; j < bytes[i].length; j += 2) {
      const code = parseInt(bytes[i].substr(j, 2), 16);
      ascii += (code >= 32 && code < 127) ? String.fromCharCode(code) : '.';
    }
    // Use BigInt for safe address arithmetic on large files
    const addr = BigInt(i) * 16n;
    const addrHex = addr.toString(16).padStart(8, '0');
    result += `${addrHex}  ${hexLine.padEnd(48)}  ${ascii}\n`;
  }
  return result;
}

// Update doc count from stats endpoint
async function updateDocCount() {
  try {
    const resp = await fetch('/v1/stats');
    const data = await resp.json();
    document.getElementById('docCount').textContent = data.doc_count;
  } catch (err) {
    console.error('Failed to fetch stats:', err);
  }
}

// Page load: update stats
document.addEventListener('DOMContentLoaded', updateDocCount);
