import { useState, useEffect, useCallback } from 'react'
import type { ApplicationSummary, ApplicationDetailResponse } from '../types'
import { api, ApiError } from '../api/client'
import { ApplicationTable } from '../components/ApplicationTable'
import { ApplicationDetail } from '../components/ApplicationDetail'
import './ApplicationsPage.css'

export function ApplicationsPage() {
  const [applications, setApplications] = useState<ApplicationSummary[]>([])
  const [listLoading, setListLoading] = useState(true)
  const [listError, setListError] = useState<string | null>(null)

  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [detail, setDetail] = useState<ApplicationDetailResponse | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState<string | null>(null)

  // Load application list on mount
  useEffect(() => {
    let cancelled = false
    setListLoading(true)
    setListError(null)

    api.listApplications()
      .then((res) => {
        if (!cancelled) {
          setApplications(res.items)
          setListLoading(false)
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setListError(err instanceof ApiError ? err.message : 'Unexpected error.')
          setListLoading(false)
        }
      })

    return () => { cancelled = true }
  }, [])

  // Load detail when selection changes
  const handleSelect = useCallback((id: string) => {
    setSelectedId(id)
    setDetailLoading(true)
    setDetailError(null)
    setDetail(null)

    api.getApplication(id)
      .then((res) => {
        setDetail(res)
        setDetailLoading(false)
      })
      .catch((err) => {
        setDetailError(err instanceof ApiError ? err.message : 'Unexpected error.')
        setDetailLoading(false)
      })
  }, [])

  const handleClose = useCallback(() => {
    setSelectedId(null)
    setDetail(null)
    setDetailError(null)
  }, [])

  return (
    <div className="applications-page">
      {/* Page header */}
      <header className="applications-page__header">
        <div className="applications-page__header-left">
          <h1 className="applications-page__title">Applications</h1>
          {!listLoading && !listError && (
            <span className="applications-page__count">
              {applications.length} application{applications.length !== 1 ? 's' : ''}
            </span>
          )}
        </div>
        <div className="applications-page__header-right">
          <button
            className="applications-page__action-btn"
            disabled
            title="Upload — not yet implemented"
            id="btn-upload-disabled"
            aria-disabled="true"
          >
            Upload Application
          </button>
        </div>
      </header>

      {/* Main content */}
      <div className="applications-page__body">
        <div className="applications-page__table-area">
          <ApplicationTable
            applications={applications}
            selectedId={selectedId}
            onSelect={handleSelect}
            loading={listLoading}
            error={listError}
          />
        </div>

        {/* Detail panel — only rendered when an item is selected or loading */}
        {(selectedId !== null || detailLoading) && (
          <ApplicationDetail
            detail={detail}
            loading={detailLoading}
            error={detailError}
            onClose={handleClose}
          />
        )}
      </div>
    </div>
  )
}
