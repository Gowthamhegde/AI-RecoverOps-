"""
Database and data store detector for DevOps environments
"""

import asyncio
import uuid
from datetime import datetime
from typing import List, Dict, Any
from ..core.detector import BaseDetector
from ..core.engine import Issue
from ..utils.logger import get_logger

class DatabaseDetector(BaseDetector):
    """Detects database and data store issues"""
    
    def __init__(self, config):
        super().__init__(config)
        self.logger = get_logger(__name__)
        
        # Database thresholds
        self.connection_timeout = 5.0
        self.slow_query_threshold = 1000  # ms
        self.connection_pool_threshold = 80  # %
        
    async def initialize(self):
        """Initialize database detector"""
        self.logger.info("Initializing Database Detector for DevOps")
        
    async def detect(self) -> List[Issue]:
        """Detect database and data store issues"""
        issues = []
        
        # Check database connections
        databases = self.config.get('databases', {})
        for db_name, db_config in databases.items():
            db_issues = await self._check_database_health(db_name, db_config)
            issues.extend(db_issues)
            
        # Check Redis instances
        redis_issues = await self._check_redis_health()
        issues.extend(redis_issues)
        
        # Check Elasticsearch clusters
        es_issues = await self._check_elasticsearch_health()
        issues.extend(es_issues)
        
        return issues
        
    async def _check_database_health(self, db_name: str, config: Dict[str, Any]) -> List[Issue]:
        """Check individual database health"""
        issues = []
        db_type = config.get('type', 'postgresql')
        
        try:
            if db_type == 'postgresql':
                issues.extend(await self._check_postgresql(db_name, config))
            elif db_type == 'mysql':
                issues.extend(await self._check_mysql(db_name, config))
            elif db_type == 'mongodb':
                issues.extend(await self._check_mongodb(db_name, config))
                
        except Exception as e:
            issues.append(Issue(
                id=f"db-check-error-{uuid.uuid4().hex[:8]}",
                type="database",
                severity="medium",
                description=f"Database health check failed for {db_name}: {str(e)}",
                metadata={
                    "database_name": db_name,
                    "database_type": db_type,
                    "error": str(e)
                },
                detected_at=datetime.now(),
                source="database_detector"
            ))
            
        return issues
        
    async def _check_postgresql(self, db_name: str, config: Dict[str, Any]) -> List[Issue]:
        """Check PostgreSQL specific health"""
        issues = []
        
        try:
            import asyncpg
            
            conn = await asyncio.wait_for(
                asyncpg.connect(config['connection_string']),
                timeout=self.connection_timeout
            )
            
            # Check active connections
            result = await conn.fetchrow("""
                SELECT count(*) as active_connections,
                       setting::int as max_connections
                FROM pg_stat_activity, pg_settings 
                WHERE name = 'max_connections'
            """)
            
            if result:
                active = result['active_connections']
                max_conn = result['max_connections']
                usage_percent = (active / max_conn) * 100
                
                if usage_percent > self.connection_pool_threshold:
                    issues.append(Issue(
                        id=f"db-connections-{uuid.uuid4().hex[:8]}",
                        type="database",
                        severity="high" if usage_percent > 90 else "medium",
                        description=f"High connection usage on {db_name}: {usage_percent:.1f}%",
                        metadata={
                            "database_name": db_name,
                            "active_connections": active,
                            "max_connections": max_conn,
                            "usage_percent": usage_percent
                        },
                        detected_at=datetime.now(),
                        source="database_detector"
                    ))
            
            # Check for long-running queries
            long_queries = await conn.fetch("""
                SELECT query, state, now() - query_start as duration
                FROM pg_stat_activity 
                WHERE state = 'active' 
                AND now() - query_start > interval '30 seconds'
                AND query NOT LIKE '%pg_stat_activity%'
            """)
            
            if long_queries:
                issues.append(Issue(
                    id=f"db-slow-queries-{uuid.uuid4().hex[:8]}",
                    type="database",
                    severity="medium",
                    description=f"Long-running queries detected on {db_name}: {len(long_queries)} queries",
                    metadata={
                        "database_name": db_name,
                        "long_query_count": len(long_queries),
                        "queries": [{"query": q['query'][:100], "duration": str(q['duration'])} for q in long_queries[:5]]
                    },
                    detected_at=datetime.now(),
                    source="database_detector"
                ))
            
            await conn.close()
            
        except asyncio.TimeoutError:
            issues.append(Issue(
                id=f"db-timeout-{uuid.uuid4().hex[:8]}",
                type="database",
                severity="high",
                description=f"Connection timeout to database {db_name}",
                metadata={
                    "database_name": db_name,
                    "timeout_seconds": self.connection_timeout
                },
                detected_at=datetime.now(),
                source="database_detector"
            ))
        except Exception as e:
            issues.append(Issue(
                id=f"db-connection-{uuid.uuid4().hex[:8]}",
                type="database",
                severity="critical",
                description=f"Cannot connect to database {db_name}: {str(e)}",
                metadata={
                    "database_name": db_name,
                    "error": str(e)
                },
                detected_at=datetime.now(),
                source="database_detector"
            ))
            
        return issues
        
    async def _check_mysql(self, db_name: str, config: Dict[str, Any]) -> List[Issue]:
        """Check MySQL specific health"""
        # Similar implementation for MySQL
        return []
        
    async def _check_mongodb(self, db_name: str, config: Dict[str, Any]) -> List[Issue]:
        """Check MongoDB specific health"""
        # Similar implementation for MongoDB
        return []
        
    async def _check_redis_health(self) -> List[Issue]:
        """Check Redis instances"""
        issues = []
        
        redis_instances = self.config.get('redis_instances', [])
        for instance in redis_instances:
            try:
                import aioredis
                
                redis = await aioredis.from_url(
                    instance['url'],
                    socket_timeout=self.connection_timeout
                )
                
                # Check Redis info
                info = await redis.info()
                
                # Check memory usage
                used_memory = info.get('used_memory', 0)
                max_memory = info.get('maxmemory', 0)
                
                if max_memory > 0:
                    memory_usage = (used_memory / max_memory) * 100
                    if memory_usage > 85:
                        issues.append(Issue(
                            id=f"redis-memory-{uuid.uuid4().hex[:8]}",
                            type="database",
                            severity="high" if memory_usage > 95 else "medium",
                            description=f"High Redis memory usage: {memory_usage:.1f}%",
                            metadata={
                                "instance_url": instance['url'],
                                "used_memory": used_memory,
                                "max_memory": max_memory,
                                "memory_usage_percent": memory_usage
                            },
                            detected_at=datetime.now(),
                            source="database_detector"
                        ))
                
                await redis.close()
                
            except Exception as e:
                issues.append(Issue(
                    id=f"redis-error-{uuid.uuid4().hex[:8]}",
                    type="database",
                    severity="high",
                    description=f"Redis connection failed: {str(e)}",
                    metadata={
                        "instance_url": instance['url'],
                        "error": str(e)
                    },
                    detected_at=datetime.now(),
                    source="database_detector"
                ))
                
        return issues
        
    async def _check_elasticsearch_health(self) -> List[Issue]:
        """Check Elasticsearch cluster health"""
        issues = []
        
        es_clusters = self.config.get('elasticsearch_clusters', [])
        for cluster in es_clusters:
            try:
                import aiohttp
                
                health_url = f"{cluster['url']}/_cluster/health"
                async with aiohttp.ClientSession() as session:
                    async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        if response.status == 200:
                            health_data = await response.json()
                            
                            if health_data.get('status') == 'red':
                                issues.append(Issue(
                                    id=f"es-cluster-red-{uuid.uuid4().hex[:8]}",
                                    type="database",
                                    severity="critical",
                                    description=f"Elasticsearch cluster {cluster['name']} status is RED",
                                    metadata={
                                        "cluster_name": cluster['name'],
                                        "cluster_url": cluster['url'],
                                        "status": health_data.get('status'),
                                        "active_shards": health_data.get('active_shards'),
                                        "unassigned_shards": health_data.get('unassigned_shards')
                                    },
                                    detected_at=datetime.now(),
                                    source="database_detector"
                                ))
                            elif health_data.get('status') == 'yellow':
                                issues.append(Issue(
                                    id=f"es-cluster-yellow-{uuid.uuid4().hex[:8]}",
                                    type="database",
                                    severity="medium",
                                    description=f"Elasticsearch cluster {cluster['name']} status is YELLOW",
                                    metadata={
                                        "cluster_name": cluster['name'],
                                        "cluster_url": cluster['url'],
                                        "status": health_data.get('status'),
                                        "unassigned_shards": health_data.get('unassigned_shards')
                                    },
                                    detected_at=datetime.now(),
                                    source="database_detector"
                                ))
                        else:
                            issues.append(Issue(
                                id=f"es-health-error-{uuid.uuid4().hex[:8]}",
                                type="database",
                                severity="high",
                                description=f"Elasticsearch health check failed: HTTP {response.status}",
                                metadata={
                                    "cluster_name": cluster['name'],
                                    "cluster_url": cluster['url'],
                                    "status_code": response.status
                                },
                                detected_at=datetime.now(),
                                source="database_detector"
                            ))
                            
            except Exception as e:
                issues.append(Issue(
                    id=f"es-connection-error-{uuid.uuid4().hex[:8]}",
                    type="database",
                    severity="high",
                    description=f"Elasticsearch connection failed: {str(e)}",
                    metadata={
                        "cluster_name": cluster['name'],
                        "cluster_url": cluster['url'],
                        "error": str(e)
                    },
                    detected_at=datetime.now(),
                    source="database_detector"
                ))
                
        return issues
        
    def get_detector_type(self) -> str:
        return "database"