//
//  PCPriceAPI.swift
//  Ejemplo de integración completa para iOS
//
//  Created by PC Price Scraper
//  API: github.com/tu-usuario/pc-price-scraper
//

import Foundation

// MARK: - Models

struct ProductResponse: Codable {
    let count: Int
    let products: [Product]
}

struct Product: Codable, Identifiable {
    let id: Int
    let name: String
    let brand: String
    let type: String
    let priceUsd: Double
    let pricePen: Double?
    let stock: String
    let store: String
    let url: String?
    let updated: String?
    
    enum CodingKeys: String, CodingKey {
        case id, name, brand, type, stock, store, url, updated
        case priceUsd = "price_usd"
        case pricePen = "price_pen"
    }
    
    var displayPrice: String {
        if let pen = pricePen {
            return String(format: "$%.2f / S/%.2f", priceUsd, pen)
        }
        return String(format: "$%.2f", priceUsd)
    }
    
    var stockStatus: StockStatus {
        switch stock.lowercased() {
        case "high": return .high
        case "medium": return .medium
        case "low": return .low
        case "out_of_stock": return .outOfStock
        default: return .unknown
        }
    }
}

enum StockStatus {
    case high, medium, low, outOfStock, unknown
    
    var displayText: String {
        switch self {
        case .high: return "En Stock"
        case .medium: return "Stock Limitado"
        case .low: return "Últimas Unidades"
        case .outOfStock: return "Agotado"
        case .unknown: return "Consultar"
        }
    }
    
    var color: String {
        switch self {
        case .high: return "green"
        case .medium: return "orange"
        case .low: return "red"
        case .outOfStock: return "gray"
        case .unknown: return "blue"
        }
    }
}

struct ComparisonResponse: Codable {
    let productName: String
    let totalStores: Int
    let matches: [ProductMatch]
    let lowestPrice: PriceDetail
    let highestPrice: PriceDetail
    let priceDifferenceUsd: Double
    let savingsPercentage: Double
    
    enum CodingKeys: String, CodingKey {
        case matches
        case productName = "product_name"
        case totalStores = "total_stores"
        case lowestPrice = "lowest_price"
        case highestPrice = "highest_price"
        case priceDifferenceUsd = "price_difference_usd"
        case savingsPercentage = "savings_percentage"
    }
}

struct ProductMatch: Codable {
    let id: Int
    let name: String
    let brand: String
    let priceUsd: Double
    let priceLocal: Double?
    let stock: String
    let store: String
    let sourceUrl: String?
    let matchConfidence: Double
    
    enum CodingKeys: String, CodingKey {
        case id, name, brand, stock, store
        case priceUsd = "price_usd"
        case priceLocal = "price_local"
        case sourceUrl = "source_url"
        case matchConfidence = "match_confidence"
    }
}

struct PriceDetail: Codable {
    let store: String
    let priceUsd: Double
    let priceLocal: Double?
    let url: String?
    let stock: String?
    
    enum CodingKeys: String, CodingKey {
        case store, url, stock
        case priceUsd = "price_usd"
        case priceLocal = "price_local"
    }
}

struct QuickComparison: Codable {
    let product: ProductSummary
    let alternatives: [Alternative]
}

struct ProductSummary: Codable {
    let id: Int
    let name: String
    let priceUsd: Double
    let store: String
    
    enum CodingKeys: String, CodingKey {
        case id, name, store
        case priceUsd = "price_usd"
    }
}

struct Alternative: Codable {
    let id: Int
    let name: String
    let priceUsd: Double
    let priceDiff: Double
    let store: String
    let url: String?
    let confidence: Double
    
    enum CodingKeys: String, CodingKey {
        case id, name, store, url, confidence
        case priceUsd = "price_usd"
        case priceDiff = "price_diff"
    }
}

// MARK: - API Service

class PCPriceAPI {
    static let shared = PCPriceAPI()
    
    // CAMBIAR ESTO según tu configuración
    private let baseURL = "http://localhost:8000/api"
    
    // Para testing en dispositivo real, usa:
    // private let baseURL = "http://192.168.1.XX:8000/api"
    
    // Para producción, usa:
    // private let baseURL = "https://tu-servidor.com/api"
    
    private init() {}
    
    // MARK: - Latest Products
    
    func getLatestProducts(
        limit: Int = 20,
        componentType: String? = nil,
        completion: @escaping (Result<ProductResponse, Error>) -> Void
    ) {
        var components = URLComponents(string: "\(baseURL)/mobile/latest")!
        components.queryItems = [
            URLQueryItem(name: "limit", value: "\(limit)")
        ]
        
        if let type = componentType {
            components.queryItems?.append(
                URLQueryItem(name: "component_type", value: type)
            )
        }
        
        performRequest(url: components.url!, completion: completion)
    }
    
    // MARK: - Best Deals
    
    func getBestDeals(
        limit: Int = 10,
        componentType: String? = nil,
        completion: @escaping (Result<ProductResponse, Error>) -> Void
    ) {
        var components = URLComponents(string: "\(baseURL)/mobile/best-deals")!
        components.queryItems = [
            URLQueryItem(name: "limit", value: "\(limit)")
        ]
        
        if let type = componentType {
            components.queryItems?.append(
                URLQueryItem(name: "component_type", value: type)
            )
        }
        
        performRequest(url: components.url!, completion: completion)
    }
    
    // MARK: - Compare Product
    
    func compareProduct(
        name: String,
        componentType: String? = nil,
        completion: @escaping (Result<ComparisonResponse, Error>) -> Void
    ) {
        let encodedName = name.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed)!
        var components = URLComponents(string: "\(baseURL)/compare/\(encodedName)")!
        
        if let type = componentType {
            components.queryItems = [
                URLQueryItem(name: "component_type", value: type)
            ]
        }
        
        performRequest(url: components.url!, completion: completion)
    }
    
    // MARK: - Quick Compare
    
    func quickCompare(
        productId: Int,
        completion: @escaping (Result<QuickComparison, Error>) -> Void
    ) {
        let url = URL(string: "\(baseURL)/mobile/compare-quick/\(productId)")!
        performRequest(url: url, completion: completion)
    }
    
    // MARK: - Search
    
    func searchProducts(
        query: String,
        limit: Int = 20,
        completion: @escaping (Result<ProductResponse, Error>) -> Void
    ) {
        var components = URLComponents(string: "\(baseURL)/search")!
        components.queryItems = [
            URLQueryItem(name: "query", value: query),
            URLQueryItem(name: "limit", value: "\(limit)")
        ]
        
        performRequest(url: components.url!, completion: completion)
    }
    
    // MARK: - Health Check
    
    func healthCheck(completion: @escaping (Result<[String: Any], Error>) -> Void) {
        let url = URL(string: "\(baseURL)/health")!
        
        URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "No data", code: -1)))
                return
            }
            
            do {
                let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
                completion(.success(json ?? [:]))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    
    // MARK: - Generic Request Handler
    
    private func performRequest<T: Decodable>(
        url: URL,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        URLSession.shared.dataTask(with: url) { data, response, error in
            if let error = error {
                DispatchQueue.main.async {
                    completion(.failure(error))
                }
                return
            }
            
            guard let httpResponse = response as? HTTPURLResponse else {
                DispatchQueue.main.async {
                    completion(.failure(NSError(domain: "Invalid response", code: -1)))
                }
                return
            }
            
            guard (200...299).contains(httpResponse.statusCode) else {
                DispatchQueue.main.async {
                    completion(.failure(NSError(
                        domain: "HTTP Error",
                        code: httpResponse.statusCode,
                        userInfo: [NSLocalizedDescriptionKey: "Status code: \(httpResponse.statusCode)"]
                    )))
                }
                return
            }
            
            guard let data = data else {
                DispatchQueue.main.async {
                    completion(.failure(NSError(domain: "No data", code: -1)))
                }
                return
            }
            
            do {
                let decoder = JSONDecoder()
                let result = try decoder.decode(T.self, from: data)
                DispatchQueue.main.async {
                    completion(.success(result))
                }
            } catch {
                print("Decoding error: \(error)")
                if let json = try? JSONSerialization.jsonObject(with: data) {
                    print("Response JSON: \(json)")
                }
                DispatchQueue.main.async {
                    completion(.failure(error))
                }
            }
        }.resume()
    }
}

// MARK: - SwiftUI Example View

/*
import SwiftUI

struct ProductListView: View {
    @StateObject private var viewModel = ProductListViewModel()
    
    var body: some View {
        NavigationView {
            List {
                if viewModel.isLoading {
                    ProgressView()
                } else {
                    ForEach(viewModel.products) { product in
                        ProductRowView(product: product)
                    }
                }
            }
            .navigationTitle("PC Components")
            .onAppear {
                viewModel.loadProducts()
            }
            .refreshable {
                await viewModel.refresh()
            }
        }
    }
}

struct ProductRowView: View {
    let product: Product
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(product.name)
                .font(.headline)
                .lineLimit(2)
            
            HStack {
                Text(product.brand)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                Text(product.displayPrice)
                    .font(.title3)
                    .bold()
            }
            
            HStack {
                Text(product.store)
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(4)
                
                Text(product.stockStatus.displayText)
                    .font(.caption)
                    .foregroundColor(stockColor(for: product.stockStatus))
            }
        }
        .padding(.vertical, 4)
    }
    
    private func stockColor(for status: StockStatus) -> Color {
        switch status {
        case .high: return .green
        case .medium: return .orange
        case .low: return .red
        case .outOfStock: return .gray
        case .unknown: return .blue
        }
    }
}

class ProductListViewModel: ObservableObject {
    @Published var products: [Product] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    func loadProducts() {
        isLoading = true
        
        PCPriceAPI.shared.getLatestProducts(limit: 50) { [weak self] result in
            self?.isLoading = false
            
            switch result {
            case .success(let response):
                self?.products = response.products
                
            case .failure(let error):
                self?.errorMessage = error.localizedDescription
                print("Error loading products: \(error)")
            }
        }
    }
    
    func refresh() async {
        await withCheckedContinuation { continuation in
            loadProducts()
            continuation.resume()
        }
    }
}
*/
